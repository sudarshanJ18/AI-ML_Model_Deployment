@echo off
REM Face Recognition Application - Windows Deployment Script
REM This script deploys the complete face recognition application to Kubernetes

setlocal enabledelayedexpansion

REM Colors for output (Windows doesn't support colors in batch files easily)
set "GREEN=[32m"
set "RED=[31m"
set "YELLOW=[33m"
set "NC=[0m"

REM Configuration
set "NAMESPACE=face-recognition"
set "DOCKER_REGISTRY=your-dockerhub-username"
set "BACKEND_IMAGE=%DOCKER_REGISTRY%/face-recognition-backend:latest"
set "FRONTEND_IMAGE=%DOCKER_REGISTRY%/face-recognition-frontend:latest"

echo Starting Face Recognition Application Deployment

REM Function to check if kubectl is available
:check_kubectl
kubectl version --client >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: kubectl is not installed or not in PATH
    exit /b 1
)
echo ✓ kubectl is available
goto :eof

REM Function to check if Docker is available
:check_docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker is not installed or not in PATH
    exit /b 1
)
echo ✓ Docker is available
goto :eof

REM Function to build and push Docker images
:build_and_push_images
echo Building and pushing Docker images...

echo Building backend image...
cd backend
docker build -t %BACKEND_IMAGE% .
docker push %BACKEND_IMAGE%
cd ..

echo Building frontend image...
cd frontend
docker build -t %FRONTEND_IMAGE% .
docker push %FRONTEND_IMAGE%
cd ..

echo ✓ Docker images built and pushed successfully
goto :eof

REM Function to deploy to Kubernetes
:deploy_k8s
echo Deploying to Kubernetes...

echo Creating namespace...
kubectl apply -f k8s/namespace.yaml

echo Creating persistent volumes...
kubectl apply -f k8s/persistent-volume.yaml

echo Creating config and secrets...
kubectl apply -f k8s/config-and-secrets.yaml

echo Deploying MongoDB...
kubectl apply -f k8s/mongodb-deployment.yaml

echo Deploying backend...
kubectl apply -f k8s/backend-deployment.yaml

echo Deploying frontend...
kubectl apply -f k8s/frontend-deployment.yaml

echo Creating services...
kubectl apply -f k8s/services.yaml

echo Creating ingress...
kubectl apply -f k8s/ingress.yaml

echo Deploying security policies...
kubectl apply -f k8s/security.yaml

echo ✓ Kubernetes deployment completed
goto :eof

REM Function to wait for deployments
:wait_for_deployments
echo Waiting for deployments to be ready...

kubectl wait --for=condition=available --timeout=300s deployment/mongodb -n %NAMESPACE%
kubectl wait --for=condition=available --timeout=300s deployment/backend -n %NAMESPACE%
kubectl wait --for=condition=available --timeout=300s deployment/frontend -n %NAMESPACE%

echo ✓ All deployments are ready
goto :eof

REM Function to show deployment status
:show_status
echo Deployment Status:
echo.
echo Pods:
kubectl get pods -n %NAMESPACE%
echo.
echo Services:
kubectl get services -n %NAMESPACE%
echo.
echo Ingress:
kubectl get ingress -n %NAMESPACE%
goto :eof

REM Function to get access information
:get_access_info
echo Access Information:
echo.
echo For Minikube:
echo Run: minikube service frontend-service -n %NAMESPACE% --url
echo.
echo For other clusters:
echo Check the ingress IP with: kubectl get ingress -n %NAMESPACE%
goto :eof

REM Function to cleanup deployment
:cleanup
echo Cleaning up deployment...
kubectl delete namespace %NAMESPACE% --ignore-not-found=true
echo ✓ Cleanup completed
goto :eof

REM Main deployment function
:deploy
echo Starting deployment process...

call :check_kubectl
call :check_docker

REM Ask user if they want to build and push images
set /p BUILD_IMAGES="Do you want to build and push Docker images? (y/n): "
if /i "%BUILD_IMAGES%"=="y" (
    call :build_and_push_images
)

call :deploy_k8s
call :wait_for_deployments

echo Deployment completed successfully!
echo.
call :show_status
echo.
call :get_access_info
goto :eof

REM Parse command line arguments
if "%1"=="deploy" goto :deploy
if "%1"=="status" goto :show_status
if "%1"=="cleanup" goto :cleanup
if "%1"=="help" goto :help
if "%1"=="" goto :deploy

echo Unknown command: %1
echo Use '%0 help' for usage information
exit /b 1

:help
echo Usage: %0 [deploy^|status^|cleanup^|help]
echo   deploy  - Deploy the application (default)
echo   status  - Show deployment status
echo   cleanup - Remove the deployment
echo   help    - Show this help message
goto :eof
