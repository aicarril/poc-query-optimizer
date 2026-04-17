#!/bin/bash
# Quick deploy script for the Kiro agent Lambda
# Usage: ./deploy.sh <KIRO_API_KEY>

set -e

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION="us-east-1"
REPO_NAME="kiro-agent-lambda"
FUNCTION_NAME="kiro-agent"
IMAGE_TAG="latest"

echo "=== Building Docker image ==="
docker build -t ${REPO_NAME}:${IMAGE_TAG} .

echo "=== Creating ECR repository (if needed) ==="
aws ecr create-repository --repository-name ${REPO_NAME} --region ${REGION} 2>/dev/null || true

echo "=== Logging into ECR ==="
aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com

echo "=== Tagging and pushing image ==="
docker tag ${REPO_NAME}:${IMAGE_TAG} ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${REPO_NAME}:${IMAGE_TAG}
docker push ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${REPO_NAME}:${IMAGE_TAG}

echo "=== Creating/updating Lambda function ==="
KIRO_API_KEY="${1:?Please provide KIRO_API_KEY as first argument}"

# Check if function exists
if aws lambda get-function --function-name ${FUNCTION_NAME} --region ${REGION} 2>/dev/null; then
    echo "Updating existing function..."
    aws lambda update-function-code \
        --function-name ${FUNCTION_NAME} \
        --image-uri ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${REPO_NAME}:${IMAGE_TAG} \
        --region ${REGION}

    aws lambda update-function-configuration \
        --function-name ${FUNCTION_NAME} \
        --timeout 900 \
        --memory-size 1024 \
        --environment "Variables={KIRO_API_KEY=${KIRO_API_KEY},AWS_REGION_NAME=${REGION}}" \
        --region ${REGION}
else
    echo "Creating new function..."

    # Create execution role if needed
    ROLE_ARN=$(aws iam get-role --role-name kiro-agent-lambda-role --query 'Role.Arn' --output text 2>/dev/null || true)

    if [ -z "$ROLE_ARN" ] || [ "$ROLE_ARN" = "None" ]; then
        echo "Creating IAM role..."
        ROLE_ARN=$(aws iam create-role \
            --role-name kiro-agent-lambda-role \
            --assume-role-policy-document '{
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }]
            }' \
            --query 'Role.Arn' --output text)

        # Attach policies
        aws iam attach-role-policy --role-name kiro-agent-lambda-role \
            --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
        aws iam attach-role-policy --role-name kiro-agent-lambda-role \
            --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess

        echo "Waiting for role to propagate..."
        sleep 10
    fi

    aws lambda create-function \
        --function-name ${FUNCTION_NAME} \
        --package-type Image \
        --code ImageUri=${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${REPO_NAME}:${IMAGE_TAG} \
        --role ${ROLE_ARN} \
        --timeout 900 \
        --memory-size 1024 \
        --environment "Variables={KIRO_API_KEY=${KIRO_API_KEY},AWS_REGION_NAME=${REGION}}" \
        --region ${REGION}
fi

echo ""
echo "=== Done! ==="
echo "Test it with:"
echo "  aws lambda invoke --function-name ${FUNCTION_NAME} --payload '{\"agent\": \"query-optimizer-agent\", \"prompt\": \"Optimize sample-code/slow_query.sql against demo_db. Target under 50ms.\"}' --cli-binary-format raw-in-base64-out /tmp/kiro-output.json --region ${REGION}"
echo "  cat /tmp/kiro-output.json | python3 -m json.tool"
