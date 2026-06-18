# AWS Lambda Container Image Deployment Plan

## Overview
Safe deployment strategy for updating a 4-year-old AWS Lambda container image with testing and rollback capability.

**Current Setup:**
- ECR Repository: `310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda`
- Region: `eu-central-1`
- Lambda Function: Uses container image from ECR
- API Gateway: Fronts the Lambda function
- Current Image: Python 3.9 (4 years old)
- New Image: Python 3.14

---

## Phase 1: Assess Current AWS Setup

### 1.1 Check Current ECR Images
```bash
# List all images in the repository
aws ecr describe-images \
  --repository-name orthodox-fasting/fastapi-lambda \
  --region eu-central-1

# Get the currently deployed image digest
aws ecr list-images \
  --repository-name orthodox-fasting/fastapi-lambda \
  --region eu-central-1
```

### 1.2 Identify Lambda Function
```bash
# List all Lambda functions to find yours
aws lambda list-functions --region eu-central-1 | grep -i "fasting\|orthodox"

# Once identified, get function details (replace FUNCTION_NAME)
aws lambda get-function --function-name FUNCTION_NAME --region eu-central-1

# Get current image URI being used
aws lambda get-function-configuration \
  --function-name FUNCTION_NAME \
  --region eu-central-1 \
  --query 'ImageUri'
```

### 1.3 Check API Gateway Configuration
```bash
# List API Gateways
aws apigateway get-rest-apis --region eu-central-1

# Get integration details (replace API_ID and RESOURCE_ID after finding them)
aws apigateway get-integration \
  --rest-api-id API_ID \
  --resource-id RESOURCE_ID \
  --http-method GET \
  --region eu-central-1
```

**Action Required:** Run these commands and note down:
- Lambda function name
- Current image URI and digest
- API Gateway ID
- Current image tag (likely `latest`)

---

## Phase 2: Build and Test New Image Locally

### 2.1 Local Build and Test
```bash
# Build the new image locally
docker build -t bgchof-test:v2 .

# Run container locally
docker run -d -p 5000:5000 --name bgchof-test bgchof-test:v2

# Wait for startup
sleep 5

# Test the API endpoints
curl http://localhost:5000/
curl http://localhost:5000/api/v1/msgForDate
curl "http://localhost:5000/api/v1/msgForDate?date=2026-05-24"

# Run integration tests
pytest tests/test_docker_integration.py -v

# Check logs for errors
docker logs bgchof-test

# Cleanup
docker stop bgchof-test
docker rm bgchof-test
```

### 2.2 Verify Breaking Changes
Test these specific scenarios:
- [ ] Root endpoint responds correctly
- [ ] API endpoint without date parameter (uses today's date)
- [ ] API endpoint with valid date parameter
- [ ] API endpoint with invalid date parameter (error handling)
- [ ] Module imports work correctly (bgchof module)
- [ ] Cache directory creation works
- [ ] Python 3.14 compatibility confirmed

---

## Phase 3: Create Backup Strategy in ECR

### 3.1 Tag Current Production Image as Backup
```bash
# Authenticate to ECR
aws ecr get-login-password --region eu-central-1 | \
  docker login --username AWS --password-stdin \
  310391119521.dkr.ecr.eu-central-1.amazonaws.com

# Pull current production image
docker pull 310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda:latest

# Tag it as backup with timestamp
docker tag \
  310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda:latest \
  310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda:backup-2026-05-24

# Push backup tag
docker push 310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda:backup-2026-05-24

# Also tag as 'production-stable' for easy reference
docker tag \
  310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda:latest \
  310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda:production-stable

docker push 310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda:production-stable
```

### 3.2 Verify Backup Created
```bash
# List all tags to confirm backup exists
aws ecr describe-images \
  --repository-name orthodox-fasting/fastapi-lambda \
  --region eu-central-1
```

---

## Phase 4: Push New Test Image to ECR

### 4.1 Build and Push Test Image
```bash
# Build new image with proper tag
docker build -t orthodox-fasting/fastapi-lambda:test-v2 .

# Tag for ECR
docker tag \
  orthodox-fasting/fastapi-lambda:test-v2 \
  310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda:test-v2

# Push to ECR
docker push 310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda:test-v2
```

### 4.2 Verify Upload
```bash
# Confirm test-v2 tag exists in ECR
aws ecr describe-images \
  --repository-name orthodox-fasting/fastapi-lambda \
  --region eu-central-1 \
  --image-ids imageTag=test-v2
```

---

## Phase 5: Create Test Lambda Function

### 5.1 Create Test Lambda Function
```bash
# Create a new Lambda function for testing (replace ROLE_ARN with your Lambda execution role)
aws lambda create-function \
  --function-name bgchof-test-v2 \
  --package-type Image \
  --code ImageUri=310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda:test-v2 \
  --role ROLE_ARN \
  --timeout 30 \
  --memory-size 512 \
  --region eu-central-1

# If you need to find your execution role ARN:
aws lambda get-function-configuration \
  --function-name PRODUCTION_FUNCTION_NAME \
  --region eu-central-1 \
  --query 'Role'
```

### 5.2 Create Test Function URL (Optional - for easy testing)
```bash
# Create a function URL for direct testing
aws lambda create-function-url-config \
  --function-name bgchof-test-v2 \
  --auth-type NONE \
  --region eu-central-1

# Get the function URL
aws lambda get-function-url-config \
  --function-name bgchof-test-v2 \
  --region eu-central-1
```

---

## Phase 6: Validate Test Lambda Function

### 6.1 Test the Lambda Function
```bash
# Invoke Lambda directly
aws lambda invoke \
  --function-name bgchof-test-v2 \
  --region eu-central-1 \
  response.json

cat response.json

# If you created a function URL, test via HTTP
curl https://YOUR_FUNCTION_URL.lambda-url.eu-central-1.on.aws/
curl https://YOUR_FUNCTION_URL.lambda-url.eu-central-1.on.aws/api/v1/msgForDate
curl "https://YOUR_FUNCTION_URL.lambda-url.eu-central-1.on.aws/api/v1/msgForDate?date=2026-05-24"
```

### 6.2 Check CloudWatch Logs
```bash
# Get recent log streams
aws logs describe-log-streams \
  --log-group-name /aws/lambda/bgchof-test-v2 \
  --region eu-central-1 \
  --order-by LastEventTime \
  --descending \
  --max-items 1

# View logs (replace LOG_STREAM_NAME)
aws logs get-log-events \
  --log-group-name /aws/lambda/bgchof-test-v2 \
  --log-stream-name LOG_STREAM_NAME \
  --region eu-central-1
```

### 6.3 Validation Checklist
- [ ] Lambda function starts without errors
- [ ] API endpoints respond correctly
- [ ] No Python 3.14 compatibility issues
- [ ] Module imports work (bgchof)
- [ ] Date calculations are accurate
- [ ] Error handling works properly
- [ ] Response times are acceptable
- [ ] No memory or timeout issues

---

## Phase 7: Update Production Lambda

### 7.1 Option A: Update Existing Lambda to Use New Image
```bash
# Update the production Lambda function to use test-v2 image
aws lambda update-function-code \
  --function-name PRODUCTION_FUNCTION_NAME \
  --image-uri 310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda:test-v2 \
  --region eu-central-1

# Wait for update to complete
aws lambda wait function-updated \
  --function-name PRODUCTION_FUNCTION_NAME \
  --region eu-central-1
```

### 7.2 Option B: Promote Test Image to Latest Tag
```bash
# Tag test-v2 as latest
docker pull 310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda:test-v2

docker tag \
  310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda:test-v2 \
  310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda:latest

docker push 310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda:latest

# Update Lambda to use latest (if it's not already configured to auto-update)
aws lambda update-function-code \
  --function-name PRODUCTION_FUNCTION_NAME \
  --image-uri 310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda:latest \
  --region eu-central-1
```

**Recommendation:** Use Option A first to test, then Option B to finalize.

---

## Phase 8: Verify Production Deployment

### 8.1 Test Production Endpoint
```bash
# Test via API Gateway (replace with your actual API Gateway URL)
curl https://YOUR_API_GATEWAY_URL/api/v1/msgForDate
curl "https://YOUR_API_GATEWAY_URL/api/v1/msgForDate?date=2026-05-24"

# Check production Lambda logs
aws logs tail /aws/lambda/PRODUCTION_FUNCTION_NAME --follow --region eu-central-1
```

### 8.2 Monitor for Issues
- [ ] Check CloudWatch metrics for errors
- [ ] Monitor response times
- [ ] Verify API Gateway integration works
- [ ] Test from actual client (nocmu.me)
- [ ] Check for any error logs

---

## Phase 9: Rollback Procedure (If Needed)

### 9.1 Quick Rollback to Stable Version
```bash
# Option 1: Rollback to production-stable tag
aws lambda update-function-code \
  --function-name PRODUCTION_FUNCTION_NAME \
  --image-uri 310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda:production-stable \
  --region eu-central-1

# Option 2: Rollback to specific backup
aws lambda update-function-code \
  --function-name PRODUCTION_FUNCTION_NAME \
  --image-uri 310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda:backup-2026-05-24 \
  --region eu-central-1

# Wait for rollback to complete
aws lambda wait function-updated \
  --function-name PRODUCTION_FUNCTION_NAME \
  --region eu-central-1

# Verify rollback successful
aws lambda get-function-configuration \
  --function-name PRODUCTION_FUNCTION_NAME \
  --region eu-central-1 \
  --query 'ImageUri'
```

### 9.2 Restore Latest Tag (If Needed)
```bash
# Pull the backup image
docker pull 310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda:production-stable

# Re-tag as latest
docker tag \
  310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda:production-stable \
  310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda:latest

# Push to restore latest tag
docker push 310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda:latest
```

---

## Phase 10: Cleanup (After Successful Deployment)

### 10.1 Remove Test Lambda Function
```bash
# Delete test Lambda function (only after production is stable)
aws lambda delete-function \
  --function-name bgchof-test-v2 \
  --region eu-central-1

# Delete function URL config if created
aws lambda delete-function-url-config \
  --function-name bgchof-test-v2 \
  --region eu-central-1
```

### 10.2 Tag Final Production Image
```bash
# Tag the successful deployment with version and date
docker pull 310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda:test-v2

docker tag \
  310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda:test-v2 \
  310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda:v2-python3.14-2026-05-24

docker push 310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda:v2-python3.14-2026-05-24
```

### 10.3 Optional: Remove Old Images
```bash
# List all images to identify old ones
aws ecr describe-images \
  --repository-name orthodox-fasting/fastapi-lambda \
  --region eu-central-1

# Delete specific old images (be careful!)
# Only do this after confirming new version is stable for several days
aws ecr batch-delete-image \
  --repository-name orthodox-fasting/fastapi-lambda \
  --region eu-central-1 \
  --image-ids imageTag=OLD_TAG_TO_DELETE
```

---

## Summary of Image Tags Strategy

| Tag | Purpose | When to Use |
|-----|---------|-------------|
| `latest` | Current production | Always points to active production image |
| `production-stable` | Last known good | Backup before any changes |
| `backup-YYYY-MM-DD` | Timestamped backup | Specific point-in-time backup |
| `test-v2` | Testing new version | Testing before production |
| `v2-python3.14-YYYY-MM-DD` | Version archive | Long-term reference |

---

## Key Safety Features

1. **Multiple Backups**: Both `production-stable` and timestamped backups
2. **Test Lambda**: Separate function for validation before production
3. **Gradual Rollout**: Test locally → Test Lambda → Production
4. **Quick Rollback**: Single command to revert to stable version
5. **No Deletion**: Keep old images until new version proven stable

---

## Estimated Timeline

- Phase 1 (Assessment): 15 minutes
- Phase 2 (Local Testing): 30 minutes
- Phase 3 (Backup): 10 minutes
- Phase 4 (Push Test Image): 10 minutes
- Phase 5 (Create Test Lambda): 10 minutes
- Phase 6 (Validate): 30 minutes
- Phase 7 (Production Update): 10 minutes
- Phase 8 (Verification): 30 minutes
- **Total: ~2.5 hours** (including buffer for issues)

---

## Troubleshooting

### Issue: Lambda function fails to start
**Solution:** Check CloudWatch logs, verify PYTHONPATH environment variable, ensure all dependencies in requirements.txt

### Issue: Module import errors
**Solution:** Verify Dockerfile PYTHONPATH setting, check that src/ directory structure is correct

### Issue: API Gateway returns 502/504
**Solution:** Check Lambda timeout settings, verify function is responding, check CloudWatch logs

### Issue: Rollback needed
**Solution:** Follow Phase 9 rollback procedure immediately

---

## Post-Deployment Monitoring

Monitor these metrics for 24-48 hours after deployment:
- Lambda invocation count
- Error rate
- Duration/latency
- Memory usage
- CloudWatch logs for errors
- API Gateway 4xx/5xx errors

---

## Notes

- Keep this document for future reference
- Document any issues encountered during deployment
- Update with actual function names and URLs after Phase 1
- Consider setting up CloudWatch alarms for production monitoring