# MCP Kubernetes Deployment

This directory contains Kubernetes manifests for deploying the MCP stack, including:
- MCP backend (FastAPI)
- PostgreSQL (dev/test)
- Redis (dev/test)
- Secrets and ConfigMap
- Ingress (optional)
- ELK stack (monitoring, dev/test)

## Prerequisites
- Kubernetes cluster (minikube, kind, or cloud)
- kubectl installed and configured
- (Optional) Ingress controller (e.g., nginx)

## Usage

1. **Create secrets and config:**
   - Edit `secret.yaml` and `configmap.yaml` to set your values (base64-encode secrets).
   - Apply:
     ```sh
     kubectl apply -f secret.yaml
     kubectl apply -f configmap.yaml
     ```

2. **Deploy databases and cache:**
   ```sh
   kubectl apply -f postgres-deployment.yaml
   kubectl apply -f redis-deployment.yaml
   ```

3. **Deploy MCP backend:**
   ```sh
   kubectl apply -f deployment.yaml
   kubectl apply -f service.yaml
   ```

4. **(Optional) Deploy ELK stack for monitoring:**
   ```sh
   kubectl apply -f elk-stack.yaml
   ```

5. **(Optional) Deploy Ingress:**
   - Edit `ingress.yaml` for your domain/TLS.
   - Apply:
     ```sh
     kubectl apply -f ingress.yaml
     ```

## Customization
- Change image tags, resource requests/limits, and environment variables as needed.
- For production, use managed Postgres/Redis/ELK or Helm charts.
- For local dev, use minikube tunnel or port-forward to access services.

## Notes
- All secrets must be base64-encoded.
- These manifests are for dev/test and reference images like `mcp-backend:latest`—build and push your image as needed.
- For production, review security, scaling, and persistence settings. 