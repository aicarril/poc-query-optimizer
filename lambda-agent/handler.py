"""Lambda handler that runs Kiro CLI in headless mode.

Triggers:
- EventBridge schedule (e.g., hourly production monitoring)
- Manual invoke with a custom prompt
- SNS/SQS for pipeline triggers

Environment variables:
- KIRO_API_KEY: Required. Kiro Pro API key for headless auth.
- AGENT_NAME: Optional. Default agent to invoke (e.g., "query-optimizer-agent").
- DEFAULT_PROMPT: Optional. Default prompt if none provided in event.
"""

import json
import logging
import os
import subprocess
from typing import Any

logger = logging.getLogger()
logger.setLevel(logging.INFO)

WORKSPACE_DIR = os.path.join(os.environ.get("LAMBDA_TASK_ROOT", "/var/task"), "workspace")


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Run a Kiro agent in headless mode."""

    # Get prompt from event or use default
    prompt = (
        event.get("prompt")
        or os.environ.get("DEFAULT_PROMPT")
        or "Run the production-monitor-agent. Check Athena query history and resource tagging."
    )

    agent = event.get("agent", os.environ.get("AGENT_NAME", ""))
    # For kiro-cli, we use --agent flag instead of /agent prefix
    agent_flag = ["--agent", agent] if agent else []

    trust_mode = event.get("trust_mode", "trust-all-tools")

    logger.info(f"Running Kiro headless with prompt: {prompt[:200]}...")

    try:
        result = subprocess.run(
            [
                "kiro-cli", "chat",
                "--no-interactive",
                f"--{trust_mode}",
                *agent_flag,
                prompt,
            ],
            capture_output=True,
            text=True,
            timeout=840,  # 14 min timeout (Lambda max is 15)
            cwd=WORKSPACE_DIR,
            env={
                **os.environ,
                "KIRO_API_KEY": os.environ["KIRO_API_KEY"],
                "HOME": "/tmp",
            },
        )

        output = result.stdout
        errors = result.stderr
        exit_code = result.returncode

        logger.info(f"Kiro CLI exited with code {exit_code}")
        if errors:
            logger.warning(f"Stderr: {errors[:500]}")

        return {
            "statusCode": 200 if exit_code == 0 else 500,
            "body": {
                "output": output,
                "errors": errors if errors else None,
                "exitCode": exit_code,
                "prompt": prompt,
            },
        }

    except subprocess.TimeoutExpired:
        logger.error("Kiro CLI timed out after 14 minutes")
        return {
            "statusCode": 504,
            "body": {
                "error": "Kiro CLI execution timed out (14 min limit)",
                "prompt": prompt,
            },
        }
    except Exception as e:
        logger.error(f"Failed to run Kiro CLI: {e}")
        return {
            "statusCode": 500,
            "body": {
                "error": str(e),
                "prompt": prompt,
            },
        }
