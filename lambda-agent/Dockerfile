FROM public.ecr.aws/lambda/python:3.12

# Install dependencies (curl-minimal is already in the base image)
RUN dnf install -y git unzip && dnf clean all

# Install Kiro CLI (non-interactive)
RUN curl -fsSL https://cli.kiro.dev/install -o /tmp/install-kiro.sh && \
    echo "y" | bash /tmp/install-kiro.sh && \
    ln -sf /root/.local/bin/kiro-cli /usr/local/bin/kiro-cli && \
    rm /tmp/install-kiro.sh

# Install uvx for AWS MCP server
RUN pip install uv && \
    ln -sf /usr/local/bin/uvx /usr/bin/uvx

# Copy agent workspace files
COPY workspace/ ${LAMBDA_TASK_ROOT}/workspace/

# Copy Lambda handler
COPY handler.py ${LAMBDA_TASK_ROOT}/

CMD ["handler.lambda_handler"]
