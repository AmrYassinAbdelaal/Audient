#!/bin/bash

# Deploy Audient to AWS ECS

set -e

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
ECR_REPOSITORY="${ECR_REPOSITORY:-audient}"
ECS_CLUSTER="${ECS_CLUSTER:-audient-cluster}"
ECS_SERVICE="${ECS_SERVICE:-audient-service}"
ECS_TASK_FAMILY="${ECS_TASK_FAMILY:-audient-task}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

echo "🚀 Deploying Audient to AWS ECS"
echo "========================================="
echo "Region: $AWS_REGION"
echo "Repository: $ECR_REPOSITORY"
echo "Cluster: $ECS_CLUSTER"
echo "Service: $ECS_SERVICE"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it first."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install it first."
    exit 1
fi

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "✅ AWS Account ID: $AWS_ACCOUNT_ID"

# Full image name
FULL_IMAGE_NAME="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}:${IMAGE_TAG}"

echo ""
echo "📦 Step 1: Building Docker image..."
cd "$(dirname "$0")/.."
docker build -f docker/Dockerfile -t ${ECR_REPOSITORY}:${IMAGE_TAG} .

echo ""
echo "🔐 Step 2: Logging in to Amazon ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

echo ""
echo "🏷️  Step 3: Tagging image..."
docker tag ${ECR_REPOSITORY}:${IMAGE_TAG} ${FULL_IMAGE_NAME}

echo ""
echo "⬆️  Step 4: Pushing image to ECR..."
docker push ${FULL_IMAGE_NAME}

echo ""
echo "🔄 Step 5: Updating ECS service..."
aws ecs update-service \
    --cluster ${ECS_CLUSTER} \
    --service ${ECS_SERVICE} \
    --force-new-deployment \
    --region ${AWS_REGION}

echo ""
echo "✅ Deployment initiated successfully!"
echo ""
echo "📊 To monitor the deployment:"
echo "   aws ecs describe-services --cluster ${ECS_CLUSTER} --services ${ECS_SERVICE} --region ${AWS_REGION}"
echo ""
echo "📝 To view logs:"
echo "   aws logs tail /ecs/${ECS_TASK_FAMILY} --follow --region ${AWS_REGION}"
echo ""

# Optional: Wait for deployment to complete
read -p "Do you want to wait for the deployment to stabilize? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "⏳ Waiting for deployment to stabilize..."
    aws ecs wait services-stable \
        --cluster ${ECS_CLUSTER} \
        --services ${ECS_SERVICE} \
        --region ${AWS_REGION}
    echo "✅ Deployment completed successfully!"
fi
