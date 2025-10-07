#!/bin/bash

# 🚀 Terry Delmonaco Automation Agent - Endpoint URL Script
# Version: 3.2

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🌐 Terry Delmonaco Automation Agent - Endpoint URLs${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Configuration
PROJECT_ID=${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null)}
REGION=${REGION:-"us-central1"}
SERVICE_NAME="td-manager-agent"

# Local development endpoints
echo -e "${GREEN}📱 Local Development Endpoints${NC}"
echo "=================================="
echo -e "${YELLOW}Base URL:${NC} http://localhost:8000"
echo ""
echo -e "${GREEN}Core Endpoints:${NC}"
echo "• ${YELLOW}API Info:${NC} http://localhost:8000/"
echo "• ${YELLOW}Health Check:${NC} http://localhost:8000/health"
echo "• ${YELLOW}Agent Status:${NC} http://localhost:8000/agents"
echo "• ${YELLOW}Performance Metrics:${NC} http://localhost:8000/metrics"
echo "• ${YELLOW}Communication Status:${NC} http://localhost:8000/communication/status"
echo "• ${YELLOW}Status Report:${NC} http://localhost:8000/status/report"
echo ""
echo -e "${GREEN}API Documentation:${NC}"
echo "• ${YELLOW}Swagger UI:${NC} http://localhost:8000/docs"
echo "• ${YELLOW}ReDoc:${NC} http://localhost:8000/redoc"
echo "• ${YELLOW}OpenAPI JSON:${NC} http://localhost:8000/openapi.json"
echo ""

# Vertex AI deployment endpoints
if [ -n "$PROJECT_ID" ]; then
    echo -e "${GREEN}☁️  Vertex AI Deployment Endpoints${NC}"
    echo "====================================="
    
    # Get the service URL from Kubernetes
    SERVICE_URL=$(kubectl get service td-manager-agent -o jsonpath='{.status.url}' 2>/dev/null)
    
    if [ -n "$SERVICE_URL" ]; then
        echo -e "${YELLOW}Base URL:${NC} ${SERVICE_URL}"
        echo ""
        echo -e "${GREEN}Core Endpoints:${NC}"
        echo "• ${YELLOW}API Info:${NC} ${SERVICE_URL}/"
        echo "• ${YELLOW}Health Check:${NC} ${SERVICE_URL}/health"
        echo "• ${YELLOW}Agent Status:${NC} ${SERVICE_URL}/agents"
        echo "• ${YELLOW}Performance Metrics:${NC} ${SERVICE_URL}/metrics"
        echo "• ${YELLOW}Communication Status:${NC} ${SERVICE_URL}/communication/status"
        echo "• ${YELLOW}Status Report:${NC} ${SERVICE_URL}/status/report"
        echo ""
        echo -e "${GREEN}API Documentation:${NC}"
        echo "• ${YELLOW}Swagger UI:${NC} ${SERVICE_URL}/docs"
        echo "• ${YELLOW}ReDoc:${NC} ${SERVICE_URL}/redoc"
        echo "• ${YELLOW}OpenAPI JSON:${NC} ${SERVICE_URL}/openapi.json"
        echo ""
    else
        echo -e "${YELLOW}⚠️  Service URL not available. Checking deployment status...${NC}"
        kubectl get pods -l app=td-manager-agent
        echo ""
        echo -e "${YELLOW}To get the service URL after deployment:${NC}"
        echo "kubectl get service td-manager-agent -o jsonpath='{.status.url}'"
        echo ""
    fi
else
    echo -e "${YELLOW}⚠️  PROJECT_ID not set. To get Vertex AI endpoints:${NC}"
    echo "export PROJECT_ID=your-gcp-project-id"
    echo "kubectl get service td-manager-agent -o jsonpath='{.status.url}'"
    echo ""
fi

# Docker Compose endpoints
echo -e "${GREEN}🐳 Docker Compose Endpoints${NC}"
echo "==============================="
echo -e "${YELLOW}Base URL:${NC} http://localhost:8000"
echo ""
echo -e "${GREEN}Services:${NC}"
echo "• ${YELLOW}Terry Delmonaco Agent:${NC} http://localhost:8000"
echo "• ${YELLOW}PostgreSQL:${NC} localhost:5432"
echo "• ${YELLOW}Redis:${NC} localhost:6379"
echo "• ${YELLOW}Prometheus:${NC} http://localhost:9090"
echo "• ${YELLOW}Grafana:${NC} http://localhost:3000"
echo ""

# Example API calls
echo -e "${GREEN}📋 Example API Calls${NC}"
echo "======================="
echo ""

echo -e "${YELLOW}Health Check:${NC}"
echo "curl http://localhost:8000/health"
echo ""

echo -e "${YELLOW}Get Agent Status:${NC}"
echo "curl http://localhost:8000/agents"
echo ""

echo -e "${YELLOW}Delegate Task:${NC}"
echo 'curl -X POST "http://localhost:8000/tasks/delegate" \
  -H "Content-Type: application/json" \
  -d '"'"'{"task_id": "test-123", "task_type": "email_processing", "priority": "routine"}'"'"
echo ""

echo -e "${YELLOW}Send Message via Google Chat:${NC}"
echo 'curl -X POST "http://localhost:8000/communication/send" \
  -H "Content-Type: application/json" \
  -d '"'"'{"platform": "google_chat", "recipient": "space-id", "message": "Hello from Terry Delmonaco Agent!"}'"'"
echo ""

echo -e "${YELLOW}Get Performance Metrics:${NC}"
echo "curl http://localhost:8000/metrics"
echo ""

# Environment-specific URLs
echo -e "${GREEN}🔧 Environment Configuration${NC}"
echo "================================"
echo ""

echo -e "${YELLOW}Local Development:${NC}"
echo "• Start local server: python app.py"
echo "• Or use Docker: docker-compose up -d"
echo ""

echo -e "${YELLOW}Vertex AI Deployment:${NC}"
echo "• Deploy: ./QUICK_DEPLOY.sh"
echo "• Get URL: kubectl get service td-manager-agent"
echo "• Port forward: kubectl port-forward service/td-manager-agent 8000:8000"
echo ""

echo -e "${GREEN}✅ Endpoint URLs retrieved successfully!${NC}"
echo ""
echo -e "${BLUE}💡 Tips:${NC}"
echo "• Use the health endpoint to verify the service is running"
echo "• Check agent status to see which agents are active"
echo "• Monitor metrics for performance insights"
echo "• Use the API documentation at /docs for detailed endpoint information" 