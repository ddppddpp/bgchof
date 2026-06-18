# Quick Start Guide: AWS Lambda Image Update

This is a condensed version of the full deployment plan. For detailed instructions, see [`AWS_DEPLOYMENT_PLAN.md`](AWS_DEPLOYMENT_PLAN.md).

## Prerequisites

- AWS CLI installed and configured
- Docker installed and running
- Access to AWS account (region: <AWS_REGION>)
- ECR repository: `<AWS_ACCOUNT_ID>.dkr.ecr.<AWS_REGION>.amazonaws.com/<REPOSITORY_NAME>`

## Quick Deployment Steps

### 1. Discover Your Setup (5 min)
```bash
# Find your Lambda function name
aws lambda list-functions --region <AWS_REGION> | grep -i "fasting\|orthodox"

# Get current image (replace <LAMBDA_FUNCTION_NAME>)
aws lambda get-function-configuration \
  --function-name <LAMBDA_FUNCTION_NAME> \
  --region <AWS_REGION> \
  --query 'ImageUri'
```

### 2. Test Locally (10 min)
```bash
# Build and test
docker build -t bgchof-test:v2 .
docker run -d -p 5000:5000 --name bgchof-test bgchof-test:v2

# Test endpoints
curl http://localhost:5000/
curl http://localhost:5000/api/v1/msgForDate
curl "http://localhost:5000/api/v1/msgForDate?date=2026-05-24"

# Run tests
pytest tests/test_docker_integration.py -v

# Cleanup
docker stop bgchof-test && docker rm bgchof-test
```

### 3. Create Backup (5 min)
```bash
# Login to ECR
aws ecr get-login-password --region <AWS_REGION> | \
  docker login --username AWS --password-stdin \
  <AWS_ACCOUNT_ID>.dkr.ecr.<AWS_REGION>.amazonaws.com

# Backup current production
docker pull <ECR_REPOSITORY_URI>:latest
docker tag \
  <ECR_REPOSITORY_URI>:latest \
  <ECR_REPOSITORY_URI>:production-stable
docker push <ECR_REPOSITORY_URI>:production-stable
```

### 4. Deploy Test Image (10 min)
```bash
# Build and push test image
docker build -t <REPOSITORY_NAME>:test-v2 .
docker tag \
  <REPOSITORY_NAME>:test-v2 \
  <ECR_REPOSITORY_URI>:test-v2
docker push <ECR_REPOSITORY_URI>:test-v2

# Update production Lambda (replace <LAMBDA_FUNCTION_NAME>)
aws lambda update-function-code \
  --function-name <LAMBDA_FUNCTION_NAME> \
  --image-uri <ECR_REPOSITORY_URI>:test-v2 \
  --region <AWS_REGION>

# Wait for update
aws lambda wait function-updated --function-name <LAMBDA_FUNCTION_NAME> --region <AWS_REGION>
```

### 5. Verify (5 min)
```bash
# Test production endpoint (replace with your API Gateway URL)
curl https://<YOUR_API_GATEWAY_URL>/api/v1/msgForDate

# Check logs
aws logs tail /aws/lambda/<LAMBDA_FUNCTION_NAME> --follow --region <AWS_REGION>
```

### 6. Rollback (If Needed)
```bash
# Quick rollback to stable version
aws lambda update-function-code \
  --function-name <LAMBDA_FUNCTION_NAME> \
  --image-uri <ECR_REPOSITORY_URI>:production-stable \
  --region <AWS_REGION>
```

### 7. Finalize (After 24h of stability)
```bash
# Promote test-v2 to latest
docker pull <ECR_REPOSITORY_URI>:test-v2
docker tag \
  <ECR_REPOSITORY_URI>:test-v2 \
  <ECR_REPOSITORY_URI>:latest
docker push <ECR_REPOSITORY_URI>:latest
```

## Key Safety Points

✅ **Backup created** before any changes (`production-stable` tag)  
✅ **Test locally** before deploying to AWS  
✅ **Test image tag** (`test-v2`) used initially  
✅ **One-command rollback** available  
✅ **Monitor for 24h** before finalizing  

## What Changed

- Python 3.9 → Python 3.14
- Base image: `python:3.9-slim-bullseye` → `python:3.14-slim-bookworm`
- All dependencies updated to latest compatible versions

## Troubleshooting

**Lambda won't start?**
→ Check CloudWatch logs: `aws logs tail /aws/lambda/<LAMBDA_FUNCTION_NAME> --follow`

**Import errors?**
→ Verify PYTHONPATH in Dockerfile: `ENV PYTHONPATH=/app/src:$PYTHONPATH`

**Need to rollback?**
→ Use the rollback command in step 6

**API Gateway errors?**
→ Check Lambda timeout settings and CloudWatch metrics

## Next Steps After Deployment

1. Monitor CloudWatch metrics for 24-48 hours
2. Test from actual client
3. If stable, promote `test-v2` to `latest` tag
4. Document any issues encountered
5. Update this guide with actual function names/URLs

## Configuration Variables

Replace these placeholders with your actual values:
- `<AWS_ACCOUNT_ID>`: Your 12-digit AWS account ID
- `<AWS_REGION>`: Your AWS region (e.g., `eu-central-1`, `us-east-1`)
- `<REPOSITORY_NAME>`: Your ECR repository name (e.g., `orthodox-fasting/fastapi-lambda`)
- `<ECR_REPOSITORY_URI>`: Full ECR URI: `<AWS_ACCOUNT_ID>.dkr.ecr.<AWS_REGION>.amazonaws.com/<REPOSITORY_NAME>`
- `<LAMBDA_FUNCTION_NAME>`: Your Lambda function name
- `<YOUR_API_GATEWAY_URL>`: Your API Gateway endpoint URL

---

**Full Documentation:** See [`AWS_DEPLOYMENT_PLAN.md`](AWS_DEPLOYMENT_PLAN.md) for complete details, troubleshooting, and advanced options.