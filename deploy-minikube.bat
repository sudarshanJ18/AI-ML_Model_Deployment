@echo off
REM Face Recognition App - Minikube Deployment Script for Windows
REM DockerHub username: jsudarshan

setlocal enabledelayedexpansion

echo 🚀 Starting Face Recognition App Deployment to Minikube
echo ==================================================

REM Configuration
set DOCKERHUB_USERNAME=jsudarshan
set APP_NAME=face-recognition
set NAMESPACE=face-recognition

REM Check prerequisites
echo [INFO] Checking prerequisites...

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker Desktop.
    exit /b 1
)

REM Check if Minikube is running
minikube status >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Minikube is not running. Starting Minikube...
    minikube start --memory=4096 --cpus=2
)

REM Check if kubectl is available
kubectl version --client >nul 2>&1
if errorlevel 1 (
    echo [ERROR] kubectl is not installed. Please install kubectl.
    exit /b 1
)

echo [SUCCESS] Prerequisites check completed

REM Build and push Docker images
echo [INFO] Building and pushing Docker images...

REM Set Docker environment to use Minikube's Docker daemon
for /f "tokens=*" %%i in ('minikube docker-env --shell cmd') do %%i

REM Build backend image
echo [INFO] Building backend image...
docker build -t %DOCKERHUB_USERNAME%/%APP_NAME%-backend:latest ./backend/

REM Build frontend image
echo [INFO] Building frontend image...
docker build -t %DOCKERHUB_USERNAME%/%APP_NAME%-frontend:latest ./frontend/

REM Push images to DockerHub
echo [INFO] Pushing images to DockerHub...
docker push %DOCKERHUB_USERNAME%/%APP_NAME%-backend:latest
docker push %DOCKERHUB_USERNAME%/%APP_NAME%-frontend:latest

echo [SUCCESS] Images built and pushed successfully

REM Create namespace
echo [INFO] Creating namespace...
kubectl create namespace %NAMESPACE% --dry-run=client -o yaml | kubectl apply -f -
echo [SUCCESS] Namespace created

REM Deploy MongoDB
echo [INFO] Deploying MongoDB...
kubectl apply -f k8s/mongodb-deployment.yaml
kubectl apply -f k8s/persistent-volume.yaml
kubectl apply -f k8s/config-and-secrets.yaml

REM Wait for MongoDB to be ready
echo [INFO] Waiting for MongoDB to be ready...
kubectl wait --for=condition=ready pod -l app=mongodb -n %NAMESPACE% --timeout=300s
echo [SUCCESS] MongoDB deployed successfully

REM Deploy backend
echo [INFO] Deploying backend...
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/services.yaml

REM Wait for backend to be ready
echo [INFO] Waiting for backend to be ready...
kubectl wait --for=condition=ready pod -l app=backend -n %NAMESPACE% --timeout=300s
echo [SUCCESS] Backend deployed successfully

REM Deploy frontend
echo [INFO] Deploying frontend...
kubectl apply -f k8s/frontend-deployment.yaml

REM Wait for frontend to be ready
echo [INFO] Waiting for frontend to be ready...
kubectl wait --for=condition=ready pod -l app=frontend -n %NAMESPACE% --timeout=300s
echo [SUCCESS] Frontend deployed successfully

REM Deploy ingress
echo [INFO] Deploying ingress...
kubectl apply -f k8s/ingress.yaml
echo [SUCCESS] Ingress deployed successfully

REM Deploy monitoring (optional)
echo [INFO] Deploying monitoring stack...
kubectl apply -f k8s/monitoring.yaml
echo [SUCCESS] Monitoring deployed successfully

REM Deploy security policies (optional)
echo [INFO] Deploying security policies...
kubectl apply -f k8s/security.yaml
echo [SUCCESS] Security policies deployed successfully

REM Get access information
echo [INFO] Getting access information...

REM Get Minikube IP
for /f "tokens=*" %%i in ('minikube ip') do set MINIKUBE_IP=%%i

echo [SUCCESS] Deployment completed successfully!
echo.
echo 🌐 Access Information:
echo =====================
echo Minikube IP: %MINIKUBE_IP%
echo.
echo 📱 Frontend:
echo   URL: http://%MINIKUBE_IP%
echo   Port: 80
echo.
echo 🔧 Backend API:
echo   URL: http://%MINIKUBE_IP%/api
echo   Health: http://%MINIKUBE_IP%/api/health
echo   Docs: http://%MINIKUBE_IP%/api/docs
echo.
echo 🗄️ MongoDB:
echo   Internal: mongodb-service:27017
echo.
echo 📊 Monitoring:
echo   Prometheus: http://%MINIKUBE_IP%:30000
echo   Grafana: http://%MINIKUBE_IP%:30001
echo.
echo 🔍 Useful Commands:
echo   kubectl get pods -n %NAMESPACE%
echo   kubectl get services -n %NAMESPACE%
echo   kubectl logs -f deployment/backend -n %NAMESPACE%
echo   kubectl logs -f deployment/frontend -n %NAMESPACE%
echo   kubectl port-forward svc/frontend-service 3000:80 -n %NAMESPACE%
echo.

pause

