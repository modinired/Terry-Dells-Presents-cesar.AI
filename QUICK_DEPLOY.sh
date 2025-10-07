#!/bin/bash

# 🚀 Terry Delmonaco Automation Agent - Quick Deploy Script
# Version: 3.2
# One-command deployment to Vertex AI

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Terry Delmonaco Automation Agent - Quick Deploy${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Configuration
PROJECT_ID=${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null)}
REGION=${REGION:-"us-central1"}
SERVICE_NAME="td-manager-agent"

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ No project ID found. Please set PROJECT_ID environment variable or run:${NC}"
    echo "gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo -e "${GREEN}✅ Project ID: ${PROJECT_ID}${NC}"
echo -e "${GREEN}✅ Region: ${REGION}${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"

# Check gcloud
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI not found. Please install Google Cloud SDK.${NC}"
    exit 1
fi

# Check docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker.${NC}"
    exit 1
fi

# Check kubectl
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl not found. Please install kubectl.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites met${NC}"
echo ""

# Authenticate and setup
echo -e "${YELLOW}🔐 Setting up Google Cloud...${NC}"

# Check authentication
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${YELLOW}Please authenticate with Google Cloud...${NC}"
    gcloud auth login
fi

# Set project
gcloud config set project ${PROJECT_ID}

# Enable APIs
echo -e "${YELLOW}📡 Enabling required APIs...${NC}"
APIs=(
    "cloudbuild.googleapis.com"
    "run.googleapis.com"
    "container.googleapis.com"
    "aiplatform.googleapis.com"
    "cloudresourcemanager.googleapis.com"
)

for api in "${APIs[@]}"; do
    echo -e "${YELLOW}Enabling ${api}...${NC}"
    gcloud services enable ${api} --project=${PROJECT_ID} --quiet
done

echo -e "${GREEN}✅ APIs enabled${NC}"
echo ""

# Build and push image
echo -e "${YELLOW}🐳 Building and pushing Docker image...${NC}"

IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Build image
echo -e "${YELLOW}Building Docker image...${NC}"
docker build -t ${IMAGE_NAME}:latest .

# Configure Docker
gcloud auth configure-docker --quiet

# Push image
echo -e "${YELLOW}Pushing to Container Registry...${NC}"
docker push ${IMAGE_NAME}:latest

echo -e "${GREEN}✅ Image pushed successfully${NC}"
echo ""

# Create secrets if not exists
echo -e "${YELLOW}🔐 Setting up secrets...${NC}"

if [ ! -f "secrets.yaml" ]; then
    echo -e "${YELLOW}Creating example secrets file...${NC}"
    cat > secrets.yaml << EOF
apiVersion: v1
kind: Secret
metadata:
  name: td-agent-secrets
type: Opaque
data:
  openai-api-key: $(echo -n "your-openai-api-key" | base64)
  database-url: $(echo -n "postgresql://user:pass@localhost/td_manager_agent" | base64)
  redis-url: $(echo -n "redis://localhost:6379" | base64)
  google-chat-api-key: $(echo -n "your-google-chat-key" | base64)
  google-chat-webhook-url: $(echo -n "https://chat.googleapis.com/v1/spaces/..." | base64)
  signal-phone-number: $(echo -n "+1234567890" | base64)
  jwt-secret: $(echo -n "your-jwt-secret" | base64)
EOF
    echo -e "${YELLOW}⚠️  Please edit secrets.yaml with your actual values before deployment${NC}"
fi

# Apply secrets
kubectl apply -f secrets.yaml --dry-run=client > /dev/null 2>&1 || {
    echo -e "${YELLOW}Creating secrets...${NC}"
    kubectl apply -f secrets.yaml
}

echo -e "${GREEN}✅ Secrets configured${NC}"
echo ""

# Deploy to Vertex AI
echo -e "${YELLOW}🚀 Deploying to Vertex AI...${NC}"

# Update deployment YAML with correct image
sed "s|gcr.io/PROJECT_ID/td-manager-agent:latest|${IMAGE_NAME}:latest|g" vertex-ai-deployment.yaml > vertex-ai-deployment-updated.yaml

# Apply deployment
kubectl apply -f vertex-ai-deployment-updated.yaml

echo -e "${GREEN}✅ Deployment applied${NC}"
echo ""

# Wait for deployment
echo -e "${YELLOW}⏳ Waiting for deployment to be ready...${NC}"

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app=td-manager-agent --timeout=300s

echo -e "${GREEN}✅ Deployment is ready${NC}"
echo ""

# Get service URL
echo -e "${YELLOW}🌐 Getting service URL...${NC}"

SERVICE_URL=$(kubectl get service td-manager-agent -o jsonpath='{.status.url}' 2>/dev/null)

if [ -n "$SERVICE_URL" ]; then
    echo -e "${GREEN}✅ Service deployed successfully${NC}"
    echo -e "${GREEN}🌐 Service URL: ${SERVICE_URL}${NC}"
else
    echo -e "${YELLOW}⚠️  Service URL not available yet. Checking pod status...${NC}"
    kubectl get pods -l app=td-manager-agent
fi

echo ""

# Health check
echo -e "${YELLOW}🏥 Performing health check...${NC}"

if [ -n "$SERVICE_URL" ]; then
    # Wait a bit for service to be fully ready
    sleep 30
    
    if curl -f "${SERVICE_URL}/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Health check passed${NC}"
    else
        echo -e "${YELLOW}⚠️  Health check failed - service may still be starting${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Skipping health check - service URL not available${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Quick deployment completed!${NC}"
echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo "1. Edit secrets.yaml with your actual API keys"
echo "2. Reapply secrets: kubectl apply -f secrets.yaml"
echo "3. Restart deployment: kubectl rollout restart deployment/td-manager-agent"
echo "4. Configure external communication platforms"
echo "5. Set up monitoring and alerting"
echo ""
echo -e "${BLUE}📊 Useful commands:${NC}"
echo "• View logs: kubectl logs -l app=td-manager-agent"
echo "• Check status: kubectl get pods -l app=td-manager-agent"
echo "• Port forward: kubectl port-forward service/td-manager-agent 8000:8000"
echo "• Delete deployment: kubectl delete -f vertex-ai-deployment-updated.yaml"
echo ""
echo -e "${BLUE}📚 Documentation:${NC}"
echo "• README.md - Complete documentation"
echo "• DEPLOYMENT_PACKAGE.md - Detailed deployment guide"
echo "• https://docs.terrydelmonaco.com - Online docs"
echo ""
echo -e "${GREEN}🚀 Terry Delmonaco Automation Agent is ready!${NC}" 