#!/bin/bash

# Face Recognition Application - Kubernetes Deployment Script
# This script deploys the complete face recognition application to Kubernetes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="face-recognition"
DOCKER_REGISTRY="your-dockerhub-username"
BACKEND_IMAGE="${DOCKER_REGISTRY}/face-recognition-backend:latest"
FRONTEND_IMAGE="${DOCKER_REGISTRY}/face-recognition-frontend:latest"

echo -e "${GREEN}Starting Face Recognition Application Deployment${NC}"

# Function to check if kubectl is available
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}Error: kubectl is not installed or not in PATH${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ kubectl is available${NC}"
}

# Function to check if Docker is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: Docker is not installed or not in PATH${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker is available${NC}"
}

# Function to build and push Docker images
build_and_push_images() {
    echo -e "${YELLOW}Building and pushing Docker images...${NC}"
    
    # Build backend image
    echo -e "${YELLOW}Building backend image...${NC}"
    cd backend
    docker build -t ${BACKEND_IMAGE} .
    docker push ${BACKEND_IMAGE}
    cd ..
    
    # Build frontend image
    echo -e "${YELLOW}Building frontend image...${NC}"
    cd frontend
    docker build -t ${FRONTEND_IMAGE} .
    docker push ${FRONTEND_IMAGE}
    cd ..
    
    echo -e "${GREEN}✓ Docker images built and pushed successfully${NC}"
}

# Function to create namespace
create_namespace() {
    echo -e "${YELLOW}Creating namespace...${NC}"
    kubectl apply -f k8s/namespace.yaml
    echo -e "${GREEN}✓ Namespace created${NC}"
}

# Function to create persistent volumes
create_persistent_volumes() {
    echo -e "${YELLOW}Creating persistent volumes...${NC}"
    kubectl apply -f k8s/persistent-volume.yaml
    echo -e "${GREEN}✓ Persistent volumes created${NC}"
}

# Function to create config and secrets
create_config_and_secrets() {
    echo -e "${YELLOW}Creating config and secrets...${NC}"
    kubectl apply -f k8s/config-and-secrets.yaml
    echo -e "${GREEN}✓ Config and secrets created${NC}"
}

# Function to deploy MongoDB
deploy_mongodb() {
    echo -e "${YELLOW}Deploying MongoDB...${NC}"
    kubectl apply -f k8s/mongodb-deployment.yaml
    echo -e "${GREEN}✓ MongoDB deployed${NC}"
}

# Function to deploy backend
deploy_backend() {
    echo -e "${YELLOW}Deploying backend...${NC}"
    kubectl apply -f k8s/backend-deployment.yaml
    echo -e "${GREEN}✓ Backend deployed${NC}"
}

# Function to deploy frontend
deploy_frontend() {
    echo -e "${YELLOW}Deploying frontend...${NC}"
    kubectl apply -f k8s/frontend-deployment.yaml
    echo -e "${GREEN}✓ Frontend deployed${NC}"
}

# Function to create services
create_services() {
    echo -e "${YELLOW}Creating services...${NC}"
    kubectl apply -f k8s/services.yaml
    echo -e "${GREEN}✓ Services created${NC}"
}

# Function to create ingress
create_ingress() {
    echo -e "${YELLOW}Creating ingress...${NC}"
    kubectl apply -f k8s/ingress.yaml
    echo -e "${GREEN}✓ Ingress created${NC}"
}

# Function to wait for deployments
wait_for_deployments() {
    echo -e "${YELLOW}Waiting for deployments to be ready...${NC}"
    
    kubectl wait --for=condition=available --timeout=300s deployment/mongodb -n ${NAMESPACE}
    kubectl wait --for=condition=available --timeout=300s deployment/backend -n ${NAMESPACE}
    kubectl wait --for=condition=available --timeout=300s deployment/frontend -n ${NAMESPACE}
    
    echo -e "${GREEN}✓ All deployments are ready${NC}"
}

# Function to show deployment status
show_status() {
    echo -e "${YELLOW}Deployment Status:${NC}"
    echo ""
    echo -e "${GREEN}Pods:${NC}"
    kubectl get pods -n ${NAMESPACE}
    echo ""
    echo -e "${GREEN}Services:${NC}"
    kubectl get services -n ${NAMESPACE}
    echo ""
    echo -e "${GREEN}Ingress:${NC}"
    kubectl get ingress -n ${NAMESPACE}
}

# Function to get access information
get_access_info() {
    echo -e "${YELLOW}Access Information:${NC}"
    echo ""
    
    # Get ingress IP
    INGRESS_IP=$(kubectl get ingress face-recognition-ingress -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "Pending")
    
    if [ "$INGRESS_IP" = "Pending" ]; then
        echo -e "${YELLOW}For Minikube:${NC}"
        echo "Run: minikube service frontend-service -n ${NAMESPACE} --url"
        echo ""
        echo -e "${YELLOW}For other clusters:${NC}"
        echo "Check the ingress IP with: kubectl get ingress -n ${NAMESPACE}"
    else
        echo -e "${GREEN}Application is accessible at: http://${INGRESS_IP}${NC}"
    fi
}

# Function to cleanup deployment
cleanup() {
    echo -e "${YELLOW}Cleaning up deployment...${NC}"
    kubectl delete namespace ${NAMESPACE} --ignore-not-found=true
    echo -e "${GREEN}✓ Cleanup completed${NC}"
}

# Main deployment function
deploy() {
    echo -e "${GREEN}Starting deployment process...${NC}"
    
    check_kubectl
    check_docker
    
    # Ask user if they want to build and push images
    read -p "Do you want to build and push Docker images? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        build_and_push_images
    fi
    
    create_namespace
    create_persistent_volumes
    create_config_and_secrets
    deploy_mongodb
    deploy_backend
    deploy_frontend
    create_services
    create_ingress
    wait_for_deployments
    
    echo -e "${GREEN}Deployment completed successfully!${NC}"
    echo ""
    show_status
    echo ""
    get_access_info
}

# Parse command line arguments
case "${1:-deploy}" in
    "deploy")
        deploy
        ;;
    "status")
        show_status
        ;;
    "cleanup")
        cleanup
        ;;
    "help")
        echo "Usage: $0 [deploy|status|cleanup|help]"
        echo "  deploy  - Deploy the application (default)"
        echo "  status  - Show deployment status"
        echo "  cleanup - Remove the deployment"
        echo "  help    - Show this help message"
        ;;
    *)
        echo "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
