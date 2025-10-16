@echo off
REM Quick Start Script for Face Recognition App on Minikube (Windows)
REM This script assumes all prerequisites are installed

echo 🚀 Quick Start: Face Recognition App on Minikube
echo ==============================================

REM Configuration
set DOCKERHUB_USERNAME=jsudarshan
set APP_NAME=face-recognition
set NAMESPACE=face-recognition

REM Step 1: Start Minikube
echo [INFO] Starting Minikube...
minikube start --memory=4096 --cpus=2

REM Step 2: Configure Docker
echo [INFO] Configuring Docker environment...
for /f "tokens=*" %%i in ('minikube docker-env --shell cmd') do %%i

REM Step 3: Build images
echo [INFO] Building Docker images...
docker build -t %DOCKERHUB_USERNAME%/%APP_NAME%-backend:latest ./backend/
docker build -t %DOCKERHUB_USERNAME%/%APP_NAME%-frontend:latest ./frontend/

REM Step 4: Push images
echo [INFO] Pushing images to DockerHub...
docker push %DOCKERHUB_USERNAME%/%APP_NAME%-backend:latest
docker push %DOCKERHUB_USERNAME%/%APP_NAME%-frontend:latest

REM Step 5: Deploy to Kubernetes
echo [INFO] Deploying to Kubernetes...

REM Create namespace
kubectl create namespace %NAMESPACE% --dry-run=client -o yaml | kubectl apply -f -

REM Deploy all resources
kubectl apply -f k8s/

REM Step 6: Wait for deployment
echo [INFO] Waiting for deployment to be ready...
kubectl wait --for=condition=ready pod -l app=mongodb -n %NAMESPACE% --timeout=300s
kubectl wait --for=condition=ready pod -l app=backend -n %NAMESPACE% --timeout=300s
kubectl wait --for=condition=ready pod -l app=frontend -n %NAMESPACE% --timeout=300s

REM Step 7: Get access information
for /f "tokens=*" %%i in ('minikube ip') do set MINIKUBE_IP=%%i

echo [SUCCESS] Deployment completed!
echo.
echo 🌐 Access your application:
echo Frontend: http://%MINIKUBE_IP%
echo Backend API: http://%MINIKUBE_IP%/api
echo API Docs: http://%MINIKUBE_IP%/api/docs
echo.
echo 🔍 Check status: kubectl get all -n %NAMESPACE%
echo 📊 View logs: kubectl logs -f deployment/backend -n %NAMESPACE%

pause

