#!/bin/bash

# Face Recognition App - Minikube Deployment Script
# DockerHub username: jsudarshan

set -e

echo "🚀 Starting Face Recognition App Deployment to Minikube"
echo "=================================================="

# Configuration
DOCKERHUB_USERNAME="jsudarshan"
APP_NAME="face-recognition"
NAMESPACE="face-recognition"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker Desktop."
        exit 1
    fi
    
    # Check if Minikube is running
    if ! minikube status > /dev/null 2>&1; then
        print_warning "Minikube is not running. Starting Minikube..."
        minikube start --memory=4096 --cpus=2
    fi
    
    # Check if kubectl is available
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed. Please install kubectl."
        exit 1
    fi
    
    print_success "Prerequisites check completed"
}

# Build and push Docker images
build_and_push_images() {
    print_status "Building and pushing Docker images..."
    
    # Set Docker environment to use Minikube's Docker daemon
    eval $(minikube docker-env)
    
    # Build backend image
    print_status "Building backend image..."
    docker build -t ${DOCKERHUB_USERNAME}/${APP_NAME}-backend:latest ./backend/
    
    # Build frontend image
    print_status "Building frontend image..."
    docker build -t ${DOCKERHUB_USERNAME}/${APP_NAME}-frontend:latest ./frontend/
    
    # Push images to DockerHub
    print_status "Pushing images to DockerHub..."
    docker push ${DOCKERHUB_USERNAME}/${APP_NAME}-backend:latest
    docker push ${DOCKERHUB_USERNAME}/${APP_NAME}-frontend:latest
    
    print_success "Images built and pushed successfully"
}

# Create namespace
create_namespace() {
    print_status "Creating namespace..."
    kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
    print_success "Namespace created"
}

# Deploy MongoDB
deploy_mongodb() {
    print_status "Deploying MongoDB..."
    kubectl apply -f k8s/mongodb-deployment.yaml
    kubectl apply -f k8s/persistent-volume.yaml
    kubectl apply -f k8s/config-and-secrets.yaml
    
    # Wait for MongoDB to be ready
    print_status "Waiting for MongoDB to be ready..."
    kubectl wait --for=condition=ready pod -l app=mongodb -n ${NAMESPACE} --timeout=300s
    print_success "MongoDB deployed successfully"
}

# Deploy backend
deploy_backend() {
    print_status "Deploying backend..."
    
    # Update image name in deployment
    sed "s|image: .*|image: ${DOCKERHUB_USERNAME}/${APP_NAME}-backend:latest|g" k8s/backend-deployment.yaml | kubectl apply -f -
    kubectl apply -f k8s/services.yaml
    
    # Wait for backend to be ready
    print_status "Waiting for backend to be ready..."
    kubectl wait --for=condition=ready pod -l app=backend -n ${NAMESPACE} --timeout=300s
    print_success "Backend deployed successfully"
}

# Deploy frontend
deploy_frontend() {
    print_status "Deploying frontend..."
    
    # Update image name in deployment
    sed "s|image: .*|image: ${DOCKERHUB_USERNAME}/${APP_NAME}-frontend:latest|g" k8s/frontend-deployment.yaml | kubectl apply -f -
    
    # Wait for frontend to be ready
    print_status "Waiting for frontend to be ready..."
    kubectl wait --for=condition=ready pod -l app=frontend -n ${NAMESPACE} --timeout=300s
    print_success "Frontend deployed successfully"
}

# Deploy ingress
deploy_ingress() {
    print_status "Deploying ingress..."
    kubectl apply -f k8s/ingress.yaml
    
    # Wait for ingress to be ready
    print_status "Waiting for ingress to be ready..."
    sleep 10
    print_success "Ingress deployed successfully"
}

# Deploy monitoring (optional)
deploy_monitoring() {
    print_status "Deploying monitoring stack..."
    kubectl apply -f k8s/monitoring.yaml
    print_success "Monitoring deployed successfully"
}

# Deploy security policies (optional)
deploy_security() {
    print_status "Deploying security policies..."
    kubectl apply -f k8s/security.yaml
    print_success "Security policies deployed successfully"
}

# Get access information
get_access_info() {
    print_status "Getting access information..."
    
    # Get Minikube IP
    MINIKUBE_IP=$(minikube ip)
    
    # Get service URLs
    print_success "Deployment completed successfully!"
    echo ""
    echo "🌐 Access Information:"
    echo "====================="
    echo "Minikube IP: ${MINIKUBE_IP}"
    echo ""
    echo "📱 Frontend:"
    echo "  URL: http://${MINIKUBE_IP}"
    echo "  Port: 80"
    echo ""
    echo "🔧 Backend API:"
    echo "  URL: http://${MINIKUBE_IP}/api"
    echo "  Health: http://${MINIKUBE_IP}/api/health"
    echo "  Docs: http://${MINIKUBE_IP}/api/docs"
    echo ""
    echo "🗄️ MongoDB:"
    echo "  Internal: mongodb-service:27017"
    echo ""
    echo "📊 Monitoring (if enabled):"
    echo "  Prometheus: http://${MINIKUBE_IP}:30000"
    echo "  Grafana: http://${MINIKUBE_IP}:30001"
    echo ""
    echo "🔍 Useful Commands:"
    echo "  kubectl get pods -n ${NAMESPACE}"
    echo "  kubectl get services -n ${NAMESPACE}"
    echo "  kubectl logs -f deployment/backend -n ${NAMESPACE}"
    echo "  kubectl logs -f deployment/frontend -n ${NAMESPACE}"
    echo "  kubectl port-forward svc/frontend-service 3000:80 -n ${NAMESPACE}"
    echo ""
}

# Cleanup function
cleanup() {
    print_status "Cleaning up resources..."
    kubectl delete namespace ${NAMESPACE} --ignore-not-found=true
    print_success "Cleanup completed"
}

# Main deployment function
main() {
    case "${1:-deploy}" in
        "deploy")
            check_prerequisites
            build_and_push_images
            create_namespace
            deploy_mongodb
            deploy_backend
            deploy_frontend
            deploy_ingress
            deploy_monitoring
            deploy_security
            get_access_info
            ;;
        "cleanup")
            cleanup
            ;;
        "status")
            kubectl get all -n ${NAMESPACE}
            ;;
        "logs")
            kubectl logs -f deployment/backend -n ${NAMESPACE}
            ;;
        *)
            echo "Usage: $0 {deploy|cleanup|status|logs}"
            echo "  deploy  - Deploy the application (default)"
            echo "  cleanup - Remove all resources"
            echo "  status  - Show deployment status"
            echo "  logs    - Show backend logs"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"

