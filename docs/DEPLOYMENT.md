# 🚀 Complete Deployment Guide

## Prerequisites

### Required Accounts
- ✅ GitHub account (for CI/CD)
- ✅ AWS account (for production infrastructure)
- ✅ PayPal Business account (gwc2780@gmail.com)
- ✅ Stripe account (for payment processing)

### Required Tools
```bash
# Docker
docker --version  # 20.10+

# Kubernetes CLI
kubectl version  # 1.28+

# AWS CLI
aws --version  # 2.0+

# Python
python3 --version  # 3.11+
```

## Step 1: Local Testing (5 minutes)

```bash
# Clone repository
git clone https://github.com/Garrettc123/revenue-agent-system.git
cd revenue-agent-system
git checkout development

# Run Quantum Revenue Engine
python3 autonomous-orchestrator/quantum-revenue-engine.py

# Expected output:
# 🌌 QUANTUM REVENUE ENGINE - UNPRECEDENTED AUTOMATION
# 📧 Payment Hub: gwc2780@gmail.com
# ⚡ Mode: ZERO-HUMAN INTERVENTION
# 🔄 Self-Healing: ENABLED
# 🚀 Auto-Scaling: ACTIVE

# In another terminal, start self-healing monitor
python3 autonomous-orchestrator/self-healing-monitor.py

# Expected output:
# 🏥 Self-Healing Monitor Started
# 📊 Monitoring 6 systems
# 🔄 Check Interval: 15 seconds
```

## Step 2: GitHub Secrets Configuration (10 minutes)

1. Go to: https://github.com/Garrettc123/revenue-agent-system/settings/secrets/actions

2. Add these secrets:

```
AWS_ACCESS_KEY_ID=<your-aws-access-key>
AWS_SECRET_ACCESS_KEY=<your-aws-secret-key>
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=<your-12-digit-account-id>

ECR_REGISTRY=<account-id>.dkr.ecr.us-east-1.amazonaws.com

PAYPAL_ACCOUNT=gwc2780@gmail.com
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...

SLACK_WEBHOOK=https://hooks.slack.com/services/...

DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0
```

## Step 3: AWS Infrastructure Setup (15 minutes)

```bash
# Configure AWS CLI
aws configure
# Enter: Access Key ID, Secret Access Key, Region (us-east-1), Output (json)

# Create ECR repository
aws ecr create-repository \
  --repository-name revenue-agent-system \
  --region us-east-1

# Create EKS cluster (this takes ~15 minutes)
aws eks create-cluster \
  --name revenue-cluster \
  --role-arn arn:aws:iam::<account-id>:role/eks-service-role \
  --resources-vpc-config subnetIds=<subnet-ids>,securityGroupIds=<sg-ids> \
  --region us-east-1

# Wait for cluster to be active
aws eks wait cluster-active --name revenue-cluster --region us-east-1

# Update kubeconfig
aws eks update-kubeconfig --region us-east-1 --name revenue-cluster

# Verify connection
kubectl get nodes
```

## Step 4: Kubernetes Configuration (5 minutes)

```bash
# Create production namespace
kubectl create namespace production

# Create secrets
kubectl create secret generic revenue-secrets \
  --from-literal=database-url="$DATABASE_URL" \
  --from-literal=openai-key="$OPENAI_API_KEY" \
  --from-literal=anthropic-key="$ANTHROPIC_API_KEY" \
  --from-literal=paypal-account="gwc2780@gmail.com" \
  --namespace=production

# Deploy Kubernetes manifests
kubectl apply -f k8s/deployment.yaml

# Check deployment status
kubectl get pods -n production
kubectl get services -n production
```

## Step 5: Trigger First Deployment (2 minutes)

```bash
# Merge development to main (triggers CI/CD)
git checkout main
git merge development
git push origin main

# Watch GitHub Actions
# Go to: https://github.com/Garrettc123/revenue-agent-system/actions

# Monitor deployment
kubectl rollout status deployment/revenue-agent-deployment -n production

# Get service URL
kubectl get service revenue-agent-service -n production
```

## Step 6: Verify System (3 minutes)

```bash
# Check pods are running
kubectl get pods -n production
# Expected: 3/3 pods Running

# Check auto-scaling is active
kubectl get hpa -n production
# Expected: revenue-agent-hpa with min=3, max=20

# Test health endpoint
LOAD_BALANCER=$(kubectl get service revenue-agent-service -n production -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
curl http://$LOAD_BALANCER/health
# Expected: {"status":"operational"}

# Check logs
kubectl logs -f deployment/revenue-agent-deployment -n production
```

## Step 7: Enable Autonomous Features (1 minute)

**Already enabled by default!**

✅ Self-healing runs every 15 minutes  
✅ Auto-scaling active (3-20 pods)  
✅ Zero-downtime deployments enabled  
✅ Revenue optimization running  
✅ Security scanning on every commit  

## Monitoring

### GitHub Actions
https://github.com/Garrettc123/revenue-agent-system/actions

### AWS CloudWatch
```bash
aws cloudwatch get-dashboard --dashboard-name revenue-agent
```

### Kubernetes Dashboard
```bash
kubectl proxy
# Access: http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/
```

## Troubleshooting

### Pods not starting
```bash
kubectl describe pod <pod-name> -n production
kubectl logs <pod-name> -n production
```

### Deployment failing
```bash
kubectl rollout history deployment/revenue-agent-deployment -n production
kubectl rollout undo deployment/revenue-agent-deployment -n production
```

### Auto-scaling not working
```bash
kubectl describe hpa revenue-agent-hpa -n production
```

## Success Checklist

- [ ] Local testing successful
- [ ] GitHub secrets configured
- [ ] AWS infrastructure deployed
- [ ] Kubernetes cluster running
- [ ] First deployment completed
- [ ] Health checks passing
- [ ] Auto-scaling active
- [ ] Self-healing enabled
- [ ] Monitoring dashboards accessible
- [ ] Payment integration tested

## Next Steps

1. Configure domain name
2. Set up SSL certificates
3. Configure payment webhooks
4. Launch marketing campaigns
5. Monitor revenue dashboard

---

**Support:** gwc2780@gmail.com  
**Status:** https://github.com/Garrettc123/revenue-agent-system/actions
