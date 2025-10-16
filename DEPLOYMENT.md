# Face Recognition Web Application - Production Deployment Guide

This document provides comprehensive instructions for deploying the Face Recognition Web Application to production using Kubernetes.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Security Considerations](#security-considerations)
4. [Deployment Steps](#deployment-steps)
5. [Monitoring and Observability](#monitoring-and-observability)
6. [Scaling and Performance](#scaling-and-performance)
7. [Backup and Recovery](#backup-and-recovery)
8. [Troubleshooting](#troubleshooting)
9. [Maintenance](#maintenance)

## Prerequisites

### Infrastructure Requirements

- **Kubernetes Cluster**: v1.21+ (minikube, kind, or cloud provider)
- **kubectl**: Configured to communicate with your cluster
- **Docker**: For building container images
- **Helm**: Optional, for advanced deployments
- **Persistent Storage**: For MongoDB data and ML models

### Resource Requirements

- **Minimum**: 4 CPU cores, 8GB RAM
- **Recommended**: 8 CPU cores, 16GB RAM
- **Storage**: 20GB+ for data and models

### Security Requirements

- TLS certificates for HTTPS
- Network policies configured
- RBAC properly set up
- Secrets management (external secret operator recommended)

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   MongoDB       │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   Database      │
│   Port: 80      │    │   Port: 8000    │    │   Port: 27017   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Monitoring    │
                    │   (Prometheus   │
                    │   + Grafana)    │
                    └─────────────────┘
```

## Security Considerations

### 1. Network Security
- All services communicate within the cluster using ClusterIP
- Network policies restrict traffic flow
- Ingress controller handles external access

### 2. Data Security
- MongoDB credentials stored in Kubernetes secrets
- API keys and tokens encrypted at rest
- Regular security updates for base images

### 3. Access Control
- RBAC policies limit pod permissions
- Service accounts with minimal required permissions
- Regular audit of access logs

## Deployment Steps

### Step 1: Prepare Environment

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd AI-ML_Model_Deployment
   ```

2. **Update configuration**:
   ```bash
   # Update Docker registry in deploy.sh
   sed -i 's/your-dockerhub-username/YOUR_ACTUAL_USERNAME/g' deploy.sh
   
   # Update image names in Kubernetes manifests
   find k8s/ -name "*.yaml" -exec sed -i 's/your-dockerhub-username/YOUR_ACTUAL_USERNAME/g' {} \;
   ```

### Step 2: Build and Push Images

```bash
# Make deploy script executable
chmod +x deploy.sh

# Build and push images (requires Docker Hub access)
./deploy.sh deploy
```

### Step 3: Deploy to Kubernetes

```bash
# Create namespace and basic resources
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/persistent-volume.yaml
kubectl apply -f k8s/config-and-secrets.yaml

# Deploy core services
kubectl apply -f k8s/mongodb-deployment.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml

# Create services and ingress
kubectl apply -f k8s/services.yaml
kubectl apply -f k8s/ingress.yaml

# Deploy security policies
kubectl apply -f k8s/security.yaml

# Deploy monitoring (optional)
kubectl apply -f k8s/monitoring.yaml
```

### Step 4: Verify Deployment

```bash
# Check pod status
kubectl get pods -n face-recognition

# Check services
kubectl get services -n face-recognition

# Check ingress
kubectl get ingress -n face-recognition

# View logs
kubectl logs -f deployment/backend -n face-recognition
```

### Step 5: Access the Application

**For Minikube**:
```bash
minikube service frontend-service -n face-recognition --url
```

**For Cloud Providers**:
```bash
# Get external IP
kubectl get ingress face-recognition-ingress -n face-recognition
```

## Monitoring and Observability

### Prometheus Metrics

The application exposes metrics at `/metrics` endpoint:
- Request count and duration
- Error rates
- Resource utilization
- Custom business metrics

### Grafana Dashboards

Access Grafana at `http://grafana-service:3000`:
- Username: `admin`
- Password: `admin123`

Pre-configured dashboards:
- Application performance
- Infrastructure metrics
- Error tracking

### Logging

- **Backend**: Structured JSON logs
- **Frontend**: Access logs via nginx
- **MongoDB**: Database operation logs

View logs:
```bash
kubectl logs -f deployment/backend -n face-recognition
kubectl logs -f deployment/frontend -n face-recognition
kubectl logs -f deployment/mongodb -n face-recognition
```

## Scaling and Performance

### Horizontal Pod Autoscaling

```bash
# Create HPA for backend
kubectl autoscale deployment backend -n face-recognition --cpu-percent=70 --min=2 --max=10

# Create HPA for frontend
kubectl autoscale deployment frontend -n face-recognition --cpu-percent=70 --min=2 --max=5
```

### Resource Optimization

**Backend**:
- CPU: 250m-500m
- Memory: 512Mi-1Gi

**Frontend**:
- CPU: 100m-200m
- Memory: 128Mi-256Mi

**MongoDB**:
- CPU: 250m-500m
- Memory: 512Mi-1Gi

### Performance Tuning

1. **Database Indexing**:
   ```javascript
   // MongoDB indexes for better performance
   db.faces.createIndex({ "name": 1 })
   db.recognition_logs.createIndex({ "timestamp": -1 })
   ```

2. **Caching**:
   - Redis for session storage
   - CDN for static assets

3. **Load Balancing**:
   - Multiple replicas
   - Session affinity if needed

## Backup and Recovery

### Database Backup

```bash
# Create backup job
kubectl create job mongodb-backup -n face-recognition --image=mongo:5.0 -- \
  mongodump --host=mongodb-service:27017 --out=/backup/$(date +%Y%m%d)

# Restore from backup
kubectl create job mongodb-restore -n face-recognition --image=mongo:5.0 -- \
  mongorestore --host=mongodb-service:27017 /backup/20240101
```

### Persistent Volume Backup

```bash
# Backup models and data
kubectl exec -it deployment/mongodb -n face-recognition -- tar -czf /backup/models.tar.gz /data/db
```

## Troubleshooting

### Common Issues

1. **Pods not starting**:
   ```bash
   kubectl describe pod <pod-name> -n face-recognition
   kubectl logs <pod-name> -n face-recognition
   ```

2. **Database connection issues**:
   ```bash
   kubectl exec -it deployment/mongodb -n face-recognition -- mongo
   ```

3. **Image pull errors**:
   ```bash
   kubectl get events -n face-recognition --sort-by='.lastTimestamp'
   ```

### Health Checks

```bash
# Check application health
curl http://<ingress-ip>/health

# Check backend readiness
curl http://<ingress-ip>/ready
```

### Debug Commands

```bash
# Get detailed pod information
kubectl describe pod <pod-name> -n face-recognition

# Execute commands in pod
kubectl exec -it <pod-name> -n face-recognition -- /bin/bash

# Port forward for local testing
kubectl port-forward service/backend-service 8000:8000 -n face-recognition
```

## Maintenance

### Updates

1. **Application Updates**:
   ```bash
   # Update image tags
   kubectl set image deployment/backend backend=new-image:tag -n face-recognition
   kubectl set image deployment/frontend frontend=new-image:tag -n face-recognition
   ```

2. **Rolling Updates**:
   ```bash
   kubectl rollout status deployment/backend -n face-recognition
   kubectl rollout undo deployment/backend -n face-recognition
   ```

### Cleanup

```bash
# Remove entire deployment
kubectl delete namespace face-recognition

# Remove specific resources
kubectl delete -f k8s/backend-deployment.yaml
```

### Security Updates

1. **Regular Updates**:
   - Base image updates
   - Dependency updates
   - Security patches

2. **Vulnerability Scanning**:
   ```bash
   # Scan images for vulnerabilities
   docker scan your-registry/face-recognition-backend:latest
   ```

## Production Checklist

- [ ] All secrets properly configured
- [ ] Network policies applied
- [ ] Resource limits set
- [ ] Health checks configured
- [ ] Monitoring enabled
- [ ] Backup strategy implemented
- [ ] SSL/TLS certificates configured
- [ ] Log aggregation set up
- [ ] Alerting configured
- [ ] Documentation updated

## Support

For issues and questions:
- Check logs: `kubectl logs -f deployment/backend -n face-recognition`
- Review events: `kubectl get events -n face-recognition`
- Monitor resources: `kubectl top pods -n face-recognition`

## License

This project is licensed under the MIT License.