# 🚀 Face Recognition App - Minikube Deployment Guide

## Prerequisites

Before deploying to Minikube, ensure you have the following installed:

### Required Software
1. **Docker Desktop** - For building and pushing images
2. **Minikube** - Local Kubernetes cluster
3. **kubectl** - Kubernetes command-line tool
4. **Git** - For cloning the repository

### Installation Commands

#### Windows (PowerShell as Administrator)
```powershell
# Install Chocolatey (if not already installed)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install required tools
choco install docker-desktop minikube kubernetes-cli git -y
```

#### macOS (using Homebrew)
```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required tools
brew install docker minikube kubectl git
```

#### Linux (Ubuntu/Debian)
```bash
# Update package list
sudo apt update

# Install Docker
sudo apt install docker.io -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# Install Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Git
sudo apt install git -y
```

## 🏗️ Deployment Steps

### Step 1: Start Required Services

#### Start Docker Desktop
- **Windows/macOS**: Launch Docker Desktop application
- **Linux**: Ensure Docker daemon is running (`sudo systemctl start docker`)

#### Start Minikube
```bash
# Start Minikube with sufficient resources
minikube start --memory=4096 --cpus=2

# Verify Minikube is running
minikube status
```

### Step 2: Configure Docker Environment

```bash
# Configure Docker to use Minikube's Docker daemon
eval $(minikube docker-env)

# Verify Docker is pointing to Minikube
docker info
```

### Step 3: Build and Push Images

#### Option A: Using the Deployment Script (Recommended)

**For Linux/macOS:**
```bash
# Make script executable
chmod +x deploy-minikube.sh

# Run deployment
./deploy-minikube.sh deploy
```

**For Windows:**
```cmd
# Run deployment script
deploy-minikube.bat
```

#### Option B: Manual Deployment

```bash
# Build backend image
docker build -t jsudarshan/face-recognition-backend:latest ./backend/

# Build frontend image
docker build -t jsudarshan/face-recognition-frontend:latest ./frontend/

# Push images to DockerHub
docker push jsudarshan/face-recognition-backend:latest
docker push jsudarshan/face-recognition-frontend:latest
```

### Step 4: Deploy to Kubernetes

```bash
# Create namespace
kubectl create namespace face-recognition

# Deploy MongoDB
kubectl apply -f k8s/mongodb-deployment.yaml
kubectl apply -f k8s/persistent-volume.yaml
kubectl apply -f k8s/config-and-secrets.yaml

# Deploy backend
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/services.yaml

# Deploy frontend
kubectl apply -f k8s/frontend-deployment.yaml

# Deploy ingress
kubectl apply -f k8s/ingress.yaml

# Deploy monitoring (optional)
kubectl apply -f k8s/monitoring.yaml

# Deploy security policies (optional)
kubectl apply -f k8s/security.yaml
```

### Step 5: Verify Deployment

```bash
# Check all resources
kubectl get all -n face-recognition

# Check pod status
kubectl get pods -n face-recognition

# Check services
kubectl get services -n face-recognition

# Check ingress
kubectl get ingress -n face-recognition
```

## 🌐 Accessing the Application

### Get Minikube IP
```bash
minikube ip
```

### Access URLs
- **Frontend**: `http://<minikube-ip>`
- **Backend API**: `http://<minikube-ip>/api`
- **API Documentation**: `http://<minikube-ip>/api/docs`
- **Health Check**: `http://<minikube-ip>/api/health`

### Port Forwarding (Alternative Access)
```bash
# Access frontend via port forwarding
kubectl port-forward svc/frontend-service 3000:80 -n face-recognition

# Access backend via port forwarding
kubectl port-forward svc/backend-service 8000:8000 -n face-recognition

# Access MongoDB via port forwarding
kubectl port-forward svc/mongodb-service 27017:27017 -n face-recognition
```

Then access:
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- MongoDB: `localhost:27017`

## 📊 Monitoring

### Prometheus
```bash
# Port forward Prometheus
kubectl port-forward svc/prometheus-service 30000:9090 -n face-recognition
```
Access: `http://localhost:30000`

### Grafana
```bash
# Port forward Grafana
kubectl port-forward svc/grafana-service 30001:3000 -n face-recognition
```
Access: `http://localhost:30001` (admin/admin)

## 🔧 Troubleshooting

### Common Issues

#### 1. Pods Not Starting
```bash
# Check pod logs
kubectl logs <pod-name> -n face-recognition

# Describe pod for events
kubectl describe pod <pod-name> -n face-recognition
```

#### 2. Image Pull Errors
```bash
# Check if images exist in DockerHub
docker pull jsudarshan/face-recognition-backend:latest
docker pull jsudarshan/face-recognition-frontend:latest

# Rebuild and push images
docker build -t jsudarshan/face-recognition-backend:latest ./backend/
docker push jsudarshan/face-recognition-backend:latest
```

#### 3. Service Connection Issues
```bash
# Check service endpoints
kubectl get endpoints -n face-recognition

# Test service connectivity
kubectl run test-pod --image=busybox -it --rm --restart=Never -- nslookup backend-service.face-recognition.svc.cluster.local
```

#### 4. Persistent Volume Issues
```bash
# Check PVC status
kubectl get pvc -n face-recognition

# Check PV status
kubectl get pv
```

### Useful Commands

```bash
# View all resources
kubectl get all -n face-recognition

# View logs
kubectl logs -f deployment/backend -n face-recognition
kubectl logs -f deployment/frontend -n face-recognition
kubectl logs -f deployment/mongodb -n face-recognition

# Scale deployments
kubectl scale deployment backend --replicas=3 -n face-recognition
kubectl scale deployment frontend --replicas=3 -n face-recognition

# Restart deployments
kubectl rollout restart deployment/backend -n face-recognition
kubectl rollout restart deployment/frontend -n face-recognition

# Delete resources
kubectl delete namespace face-recognition
```

## 🧹 Cleanup

### Remove All Resources
```bash
# Delete namespace (removes all resources)
kubectl delete namespace face-recognition

# Or use the cleanup script
./deploy-minikube.sh cleanup
```

### Stop Minikube
```bash
minikube stop
```

## 📈 Scaling

### Horizontal Pod Autoscaling
```bash
# Apply HPA for backend
kubectl apply -f k8s/hpa-backend.yaml

# Apply HPA for frontend
kubectl apply -f k8s/hpa-frontend.yaml
```

### Manual Scaling
```bash
# Scale backend to 3 replicas
kubectl scale deployment backend --replicas=3 -n face-recognition

# Scale frontend to 3 replicas
kubectl scale deployment frontend --replicas=3 -n face-recognition
```

## 🔒 Security

### Network Policies
```bash
# Apply network policies
kubectl apply -f k8s/security.yaml
```

### RBAC
```bash
# Check RBAC configuration
kubectl get roles -n face-recognition
kubectl get rolebindings -n face-recognition
```

## 📝 Notes

- The application uses in-memory storage as fallback if MongoDB is not available
- Real face recognition is implemented with MTCNN and FaceNet models
- All images are pushed to DockerHub under the `jsudarshan` namespace
- The deployment includes monitoring with Prometheus and Grafana
- Security policies are applied for network isolation

## 🆘 Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Review pod logs for error messages
3. Verify all prerequisites are installed
4. Ensure Docker images are built and pushed successfully

