# Kiro Agent Lambda

Run Kiro agents serverlessly in AWS Lambda. The same agents that run locally in Kiro IDE
run headless in a container — triggered by EventBridge, CodePipeline, or manual invoke.

## Architecture

```
EventBridge Schedule ──→ Lambda (Kiro CLI headless) ──→ AWS Resources
CodePipeline trigger ──→   ├── query-optimizer-agent     ├── Athena
Manual invoke ─────────→   ├── production-monitor-agent   ├── CloudWatch
SNS/SQS ───────────────→   ├── ci-review-agent            ├── S3
                           └── merge-agent                └── EC2/Lambda/etc
```

## Deploy

1. Start Docker Desktop
2. Get a Kiro API key from https://app.kiro.dev (requires Pro subscription)
3. Run:

```bash
cd lambda-agent
./deploy.sh <YOUR_KIRO_API_KEY>
```

## Invoke

```bash
# Query optimization
aws lambda invoke --function-name kiro-agent \
  --payload '{"agent": "query-optimizer-agent", "prompt": "Optimize sample-code/slow_query.sql against demo_db. Target under 50ms."}' \
  --cli-binary-format raw-in-base64-out \
  /tmp/kiro-output.json --region us-east-1

# Production monitoring
aws lambda invoke --function-name kiro-agent \
  --payload '{"agent": "production-monitor-agent", "prompt": "Check Athena query history, resource tagging, and running resources."}' \
  --cli-binary-format raw-in-base64-out \
  /tmp/kiro-output.json --region us-east-1

# Code review
aws lambda invoke --function-name kiro-agent \
  --payload '{"agent": "ci-review-agent", "prompt": "Review sample-code/bad_python.py against coding standards."}' \
  --cli-binary-format raw-in-base64-out \
  /tmp/kiro-output.json --region us-east-1

# View results
cat /tmp/kiro-output.json | python3 -m json.tool
```

## Schedule (EventBridge)

To run production monitoring every hour:

```bash
aws events put-rule --name kiro-hourly-monitor \
  --schedule-expression "rate(1 hour)" --region us-east-1

aws lambda add-permission --function-name kiro-agent \
  --statement-id eventbridge-invoke \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:us-east-1:$(aws sts get-caller-identity --query Account --output text):rule/kiro-hourly-monitor

aws events put-targets --rule kiro-hourly-monitor --targets '[{
  "Id": "kiro-agent",
  "Arn": "arn:aws:lambda:us-east-1:'$(aws sts get-caller-identity --query Account --output text)':function:kiro-agent",
  "Input": "{\"agent\": \"production-monitor-agent\", \"prompt\": \"Run a full production health check.\"}"
}]' --region us-east-1
```

## How It Works

1. Lambda starts with a Docker image containing Kiro CLI + agent workspace
2. The handler receives an event with `agent` and `prompt` fields
3. It runs `kiro-cli chat --no-interactive --trust-all-tools "<prompt>"` in the workspace directory
4. Kiro CLI loads the agents, steering docs, and MCP server config from the workspace
5. The agent executes (queries Athena, reviews code, etc.) and returns results
6. Lambda returns the output as JSON
