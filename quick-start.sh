#!/bin/bash

# Quick Start Script for Face Recognition App on Minikube
# This script assumes all prerequisites are installed

set -e

echo "🚀 Quick Start: Face Recognition App on Minikube"
echo "=============================================="

# Configuration
DOCKERHUB_USERNAME="jsudarshan"
APP_NAME="face-recognition"
NAMESPACE="face-recognition"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Step 1: Start Minikube
print_status "Starting Minikube..."
minikube start --memory=4096 --cpus=2

# Step 2: Configure Docker
print_status "Configuring Docker environment..."
eval $(minikube docker-env)

# Step 3: Build images
print_status "Building Docker images..."
docker build -t ${DOCKERHUB_USERNAME}/${APP_NAME}-backend:latest ./backend/
docker build -t ${DOCKERHUB_USERNAME}/${APP_NAME}-frontend:latest ./frontend/

# Step 4: Push images
print_status "Pushing images to DockerHub..."
docker push ${DOCKERHUB_USERNAME}/${APP_NAME}-backend:latest
docker push ${DOCKERHUB_USERNAME}/${APP_NAME}-frontend:latest

# Step 5: Deploy to Kubernetes
print_status "Deploying to Kubernetes..."

# Create namespace
kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -

# Deploy all resources
kubectl apply -f k8s/

# Step 6: Wait for deployment
print_status "Waiting for deployment to be ready..."
kubectl wait --for=condition=ready pod -l app=mongodb -n ${NAMESPACE} --timeout=300s
kubectl wait --for=condition=ready pod -l app=backend -n ${NAMESPACE} --timeout=300s
kubectl wait --for=condition=ready pod -l app=frontend -n ${NAMESPACE} --timeout=300s

# Step 7: Get access information
MINIKUBE_IP=$(minikube ip)

print_success "Deployment completed!"
echo ""
echo "🌐 Access your application:"
echo "Frontend: http://${MINIKUBE_IP}"
echo "Backend API: http://${MINIKUBE_IP}/api"
echo "API Docs: http://${MINIKUBE_IP}/api/docs"
echo ""
echo "🔍 Check status: kubectl get all -n ${NAMESPACE}"
echo "📊 View logs: kubectl logs -f deployment/backend -n ${NAMESPACE}"

