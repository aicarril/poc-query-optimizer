# Agent-Driven Development Pipeline POC

An automated development pipeline powered by Kiro agents that replaces traditional CI linting tools
with intelligent, context-aware code review and live AWS monitoring.

## What This Demonstrates

### 1. Automated Code Review Pipeline
Developers push to feature branches. The `ci-review-agent` validates code against team standards,
auto-fixes formatting/style issues (replacing yamllint, black, pylint), and flags anything that
needs human judgment. The `merge-agent` handles merging approved branches to main.

### 2. Live Production Monitoring
The `production-monitor-agent` connects to AWS via MCP to collect CloudWatch metrics, analyze
resource utilization, check tagging compliance, and generate recommendations. It can even push
code fixes back through the review pipeline.

### 3. Athena Query Optimization
The `query-optimizer-agent` runs queries against Athena live, measures execution time, and
iterates through optimizations (partition pruning, column pruning, JOIN reordering) until the
target of < 50ms is achieved. See `sample-code/slow_query.sql` → `optimized_query.sql`.

### 4. Live AWS Resource Access
Agents use the AWS MCP server to query Athena, pull CloudWatch metrics, discover resources,
and check compliance — all from within Kiro.

### 5. Developer Consistency
Steering docs enforce standardized coding guidelines across all developers. Every agent and
every review follows the same rules defined in `.kiro/steering/coding-standards.md`.

## Quick Start

1. Open this folder as a workspace in Kiro
2. Ensure the `aws-api` MCP server is connected (check MCP Server panel)
3. Try editing `sample-code/bad_python.py` — the review hook will trigger automatically
4. Ask Kiro: "Run the query optimizer agent on sample-code/slow_query.sql"
5. Ask Kiro: "Run the production monitor agent to check our AWS environment"

## Demo Scenarios

### Demo 1: Code Review (replaces yamllint + black)
Edit `sample-code/bad_python.py` or `sample-code/bad_config.yaml`. The hook triggers the
CI Review Agent which identifies and fixes issues automatically.

### Demo 2: Query Optimization (live Athena)
Tell Kiro: "Optimize the query in sample-code/slow_query.sql using the query optimizer agent.
Target execution time is under 50ms."

### Demo 3: Production Monitoring (live AWS)
Tell Kiro: "Run the production monitor agent. Check CloudWatch metrics, resource tagging,
and Athena query performance for the last 24 hours."

### Demo 4: Full Pipeline
1. Create a feature branch: `git checkout -b feature/demo-fix`
2. Make changes to any file
3. The CI Review Agent auto-validates
4. Tell Kiro: "Merge this branch using the merge agent"

## Project Structure

```
.kiro/
  agents/
    ci-review-agent.md           # Replaces yamllint, black, pylint
    merge-agent.md               # Handles feature branch → main merges
    production-monitor-agent.md  # Live AWS monitoring + recommendations
    query-optimizer-agent.md     # Athena query optimization to < 50ms
  hooks/
    review-on-push.json          # Auto-triggers review on code changes
    validate-yaml-on-save.json   # YAML-specific validation on save
  steering/
    coding-standards.md          # Team-wide standards (auto-included)
    project-context.md           # Pipeline architecture (auto-included)
  settings/
    mcp.json                     # AWS MCP server config
sample-code/
  bad_python.py                  # Python with intentional issues (demo)
  bad_config.yaml                # YAML/CloudFormation with issues (demo)
  slow_query.sql                 # Unoptimized Athena query (demo)
  optimized_query.sql            # What the optimizer produces (reference)
```
