#!/bin/bash

# Terry Delmonaco Automation Agent - Vertex AI Deployment Script
# Version: 3.2

set -e

# Configuration
PROJECT_ID=${PROJECT_ID:-"your-gcp-project-id"}
REGION=${REGION:-"us-central1"}
SERVICE_NAME="td-manager-agent"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Terry Delmonaco Automation Agent - Vertex AI Deployment${NC}"
echo "=================================================="

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}❌ gcloud CLI not found. Please install Google Cloud SDK.${NC}"
        exit 1
    fi
    
    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker not found. Please install Docker.${NC}"
        exit 1
    fi
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}❌ kubectl not found. Please install kubectl.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Prerequisites check passed${NC}"
}

# Authenticate with Google Cloud
authenticate_gcp() {
    echo -e "${YELLOW}Authenticating with Google Cloud...${NC}"
    
    # Check if already authenticated
    if gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        echo -e "${GREEN}✅ Already authenticated with Google Cloud${NC}"
    else
        echo -e "${YELLOW}Please authenticate with Google Cloud...${NC}"
        gcloud auth login
    fi
    
    # Set project
    gcloud config set project ${PROJECT_ID}
    echo -e "${GREEN}✅ Project set to ${PROJECT_ID}${NC}"
}

# Enable required APIs
enable_apis() {
    echo -e "${YELLOW}Enabling required Google Cloud APIs...${NC}"
    
    APIs=(
        "cloudbuild.googleapis.com"
        "run.googleapis.com"
        "container.googleapis.com"
        "aiplatform.googleapis.com"
        "cloudresourcemanager.googleapis.com"
    )
    
    for api in "${APIs[@]}"; do
        echo -e "${YELLOW}Enabling ${api}...${NC}"
        gcloud services enable ${api} --project=${PROJECT_ID}
    done
    
    echo -e "${GREEN}✅ All required APIs enabled${NC}"
}

# Build and push Docker image
build_and_push_image() {
    echo -e "${YELLOW}Building and pushing Docker image...${NC}"
    
    # Build image
    echo -e "${YELLOW}Building Docker image...${NC}"
    docker build -t ${IMAGE_NAME}:latest .
    
    # Configure Docker to use gcloud as a credential helper
    gcloud auth configure-docker
    
    # Push image
    echo -e "${YELLOW}Pushing image to Google Container Registry...${NC}"
    docker push ${IMAGE_NAME}:latest
    
    echo -e "${GREEN}✅ Docker image pushed successfully${NC}"
}

# Create secrets
create_secrets() {
    echo -e "${YELLOW}Creating Kubernetes secrets...${NC}"
    
    # Check if secrets file exists
    if [ ! -f "secrets.yaml" ]; then
        echo -e "${RED}❌ secrets.yaml not found. Please create it with your secrets.${NC}"
        echo "Example secrets.yaml:"
        cat << EOF
apiVersion: v1
kind: Secret
metadata:
  name: td-agent-secrets
type: Opaque
data:
  openai-api-key: <base64-encoded-value>
  database-url: <base64-encoded-value>
  redis-url: <base64-encoded-value>
  google-chat-api-key: <base64-encoded-value>
  google-chat-webhook-url: <base64-encoded-value>
  signal-phone-number: <base64-encoded-value>
  jwt-secret: <base64-encoded-value>
EOF
        exit 1
    fi
    
    # Apply secrets
    kubectl apply -f secrets.yaml
    echo -e "${GREEN}✅ Secrets created successfully${NC}"
}

# Deploy to Vertex AI
deploy_to_vertex_ai() {
    echo -e "${YELLOW}Deploying to Vertex AI...${NC}"
    
    # Update the deployment YAML with the correct image
    sed "s|gcr.io/PROJECT_ID/td-manager-agent:latest|${IMAGE_NAME}:latest|g" vertex-ai-deployment.yaml > vertex-ai-deployment-updated.yaml
    
    # Apply the deployment
    kubectl apply -f vertex-ai-deployment-updated.yaml
    
    echo -e "${GREEN}✅ Deployment applied successfully${NC}"
}

# Wait for deployment
wait_for_deployment() {
    echo -e "${YELLOW}Waiting for deployment to be ready...${NC}"
    
    kubectl wait --for=condition=ready pod -l app=td-manager-agent --timeout=300s
    
    echo -e "${GREEN}✅ Deployment is ready${NC}"
}

# Get service URL
get_service_url() {
    echo -e "${YELLOW}Getting service URL...${NC}"
    
    SERVICE_URL=$(kubectl get service td-manager-agent -o jsonpath='{.status.url}')
    
    if [ -n "$SERVICE_URL" ]; then
        echo -e "${GREEN}✅ Service deployed successfully${NC}"
        echo -e "${GREEN}🌐 Service URL: ${SERVICE_URL}${NC}"
    else
        echo -e "${RED}❌ Failed to get service URL${NC}"
    fi
}

# Health check
health_check() {
    echo -e "${YELLOW}Performing health check...${NC}"
    
    SERVICE_URL=$(kubectl get service td-manager-agent -o jsonpath='{.status.url}')
    
    if [ -n "$SERVICE_URL" ]; then
        # Wait a bit for the service to be fully ready
        sleep 30
        
        # Perform health check
        if curl -f "${SERVICE_URL}/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Health check passed${NC}"
        else
            echo -e "${RED}❌ Health check failed${NC}"
        fi
    else
        echo -e "${RED}❌ Service URL not available${NC}"
    fi
}

# Main deployment function
main() {
    echo -e "${GREEN}Starting deployment process...${NC}"
    
    check_prerequisites
    authenticate_gcp
    enable_apis
    build_and_push_image
    create_secrets
    deploy_to_vertex_ai
    wait_for_deployment
    get_service_url
    health_check
    
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
    echo ""
    echo -e "${GREEN}Next steps:${NC}"
    echo "1. Configure your external communication platforms (Google Chat, Signal)"
    echo "2. Set up monitoring and alerting"
    echo "3. Test the agent ecosystem"
    echo "4. Monitor logs and performance"
}

# Run main function
main "$@" 