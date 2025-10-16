#!/bin/bash

# Face Recognition Application - Test Script
# This script tests the complete deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

NAMESPACE="face-recognition"
TIMEOUT=300

echo -e "${GREEN}Starting Face Recognition Application Tests${NC}"

# Function to test Kubernetes deployment
test_k8s_deployment() {
    echo -e "${YELLOW}Testing Kubernetes deployment...${NC}"
    
    # Check if namespace exists
    if ! kubectl get namespace ${NAMESPACE} &> /dev/null; then
        echo -e "${RED}Error: Namespace ${NAMESPACE} does not exist${NC}"
        return 1
    fi
    
    # Check if all pods are running
    echo -e "${YELLOW}Checking pod status...${NC}"
    kubectl wait --for=condition=ready pod -l app=backend -n ${NAMESPACE} --timeout=${TIMEOUT}s
    kubectl wait --for=condition=ready pod -l app=frontend -n ${NAMESPACE} --timeout=${TIMEOUT}s
    kubectl wait --for=condition=ready pod -l app=mongodb -n ${NAMESPACE} --timeout=${TIMEOUT}s
    
    echo -e "${GREEN}✓ All pods are running${NC}"
    
    # Check services
    echo -e "${YELLOW}Checking services...${NC}"
    kubectl get services -n ${NAMESPACE}
    
    # Check ingress
    echo -e "${YELLOW}Checking ingress...${NC}"
    kubectl get ingress -n ${NAMESPACE}
    
    return 0
}

# Function to test API endpoints
test_api_endpoints() {
    echo -e "${YELLOW}Testing API endpoints...${NC}"
    
    # Get backend service URL
    BACKEND_URL=$(kubectl get service backend-service -n ${NAMESPACE} -o jsonpath='{.spec.clusterIP}'):8000
    
    # Test health endpoint
    echo -e "${YELLOW}Testing health endpoint...${NC}"
    kubectl run test-pod --image=curlimages/curl --rm -i --restart=Never -- \
        curl -f http://${BACKEND_URL}/health
    
    # Test ready endpoint
    echo -e "${YELLOW}Testing ready endpoint...${NC}"
    kubectl run test-pod --image=curlimages/curl --rm -i --restart=Never -- \
        curl -f http://${BACKEND_URL}/ready
    
    # Test root endpoint
    echo -e "${YELLOW}Testing root endpoint...${NC}"
    kubectl run test-pod --image=curlimages/curl --rm -i --restart=Never -- \
        curl -f http://${BACKEND_URL}/
    
    echo -e "${GREEN}✓ API endpoints are working${NC}"
    return 0
}

# Function to test database connectivity
test_database_connectivity() {
    echo -e "${YELLOW}Testing database connectivity...${NC}"
    
    # Test MongoDB connection
    kubectl exec -it deployment/mongodb -n ${NAMESPACE} -- mongo --eval "db.adminCommand('ping')"
    
    echo -e "${GREEN}✓ Database connectivity is working${NC}"
    return 0
}

# Function to test frontend
test_frontend() {
    echo -e "${YELLOW}Testing frontend...${NC}"
    
    # Get frontend service URL
    FRONTEND_URL=$(kubectl get service frontend-service -n ${NAMESPACE} -o jsonpath='{.spec.clusterIP}'):80
    
    # Test frontend health
    kubectl run test-pod --image=curlimages/curl --rm -i --restart=Never -- \
        curl -f http://${FRONTEND_URL}/health
    
    echo -e "${GREEN}✓ Frontend is working${NC}"
    return 0
}

# Function to test monitoring
test_monitoring() {
    echo -e "${YELLOW}Testing monitoring stack...${NC}"
    
    # Check if monitoring is deployed
    if kubectl get deployment prometheus -n ${NAMESPACE} &> /dev/null; then
        echo -e "${YELLOW}Testing Prometheus...${NC}"
        PROMETHEUS_URL=$(kubectl get service prometheus-service -n ${NAMESPACE} -o jsonpath='{.spec.clusterIP}'):9090
        kubectl run test-pod --image=curlimages/curl --rm -i --restart=Never -- \
            curl -f http://${PROMETHEUS_URL}/api/v1/query?query=up
    fi
    
    if kubectl get deployment grafana -n ${NAMESPACE} &> /dev/null; then
        echo -e "${YELLOW}Testing Grafana...${NC}"
        GRAFANA_URL=$(kubectl get service grafana-service -n ${NAMESPACE} -o jsonpath='{.spec.clusterIP}'):3000
        kubectl run test-pod --image=curlimages/curl --rm -i --restart=Never -- \
            curl -f http://${GRAFANA_URL}/api/health
    fi
    
    echo -e "${GREEN}✓ Monitoring stack is working${NC}"
    return 0
}

# Function to run load tests
run_load_tests() {
    echo -e "${YELLOW}Running basic load tests...${NC}"
    
    # Simple load test using curl
    BACKEND_URL=$(kubectl get service backend-service -n ${NAMESPACE} -o jsonpath='{.spec.clusterIP}'):8000
    
    for i in {1..10}; do
        kubectl run test-pod-${i} --image=curlimages/curl --rm -i --restart=Never -- \
            curl -f http://${BACKEND_URL}/health &
    done
    
    wait
    echo -e "${GREEN}✓ Load tests completed${NC}"
    return 0
}

# Function to generate test report
generate_test_report() {
    echo -e "${YELLOW}Generating test report...${NC}"
    
    REPORT_FILE="test-report-$(date +%Y%m%d-%H%M%S).txt"
    
    {
        echo "Face Recognition Application Test Report"
        echo "Generated on: $(date)"
        echo "========================================"
        echo ""
        echo "Namespace: ${NAMESPACE}"
        echo ""
        echo "Pod Status:"
        kubectl get pods -n ${NAMESPACE}
        echo ""
        echo "Service Status:"
        kubectl get services -n ${NAMESPACE}
        echo ""
        echo "Ingress Status:"
        kubectl get ingress -n ${NAMESPACE}
        echo ""
        echo "Resource Usage:"
        kubectl top pods -n ${NAMESPACE} 2>/dev/null || echo "Metrics not available"
        echo ""
        echo "Events:"
        kubectl get events -n ${NAMESPACE} --sort-by='.lastTimestamp'
    } > ${REPORT_FILE}
    
    echo -e "${GREEN}✓ Test report generated: ${REPORT_FILE}${NC}"
    return 0
}

# Main test function
run_tests() {
    echo -e "${GREEN}Running comprehensive tests...${NC}"
    
    local tests_passed=0
    local tests_failed=0
    
    # Run all tests
    if test_k8s_deployment; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    if test_api_endpoints; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    if test_database_connectivity; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    if test_frontend; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    if test_monitoring; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    if run_load_tests; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    generate_test_report
    
    echo ""
    echo -e "${GREEN}Test Summary:${NC}"
    echo -e "${GREEN}Passed: ${tests_passed}${NC}"
    echo -e "${RED}Failed: ${tests_failed}${NC}"
    
    if [ ${tests_failed} -eq 0 ]; then
        echo -e "${GREEN}All tests passed! Application is ready for production.${NC}"
        return 0
    else
        echo -e "${RED}Some tests failed. Please check the logs and fix issues.${NC}"
        return 1
    fi
}

# Parse command line arguments
case "${1:-all}" in
    "k8s")
        test_k8s_deployment
        ;;
    "api")
        test_api_endpoints
        ;;
    "db")
        test_database_connectivity
        ;;
    "frontend")
        test_frontend
        ;;
    "monitoring")
        test_monitoring
        ;;
    "load")
        run_load_tests
        ;;
    "all")
        run_tests
        ;;
    "help")
        echo "Usage: $0 [k8s|api|db|frontend|monitoring|load|all|help]"
        echo "  k8s        - Test Kubernetes deployment"
        echo "  api        - Test API endpoints"
        echo "  db         - Test database connectivity"
        echo "  frontend   - Test frontend"
        echo "  monitoring - Test monitoring stack"
        echo "  load       - Run load tests"
        echo "  all        - Run all tests (default)"
        echo "  help       - Show this help message"
        ;;
    *)
        echo "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
