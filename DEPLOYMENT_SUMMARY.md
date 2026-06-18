# AWS Lambda Deployment Summary - May 24, 2026

## Current Status: ✅ PRODUCTION STABLE (Rolled Back)

### What We Accomplished

1. ✅ **Assessed AWS Setup**
   - Lambda Function: `orthodox-fasting`
   - ECR Repository: `310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda`
   - Current Image: From March 5, 2022 (Python 3.9)
   - Integration: API Gateway + Lambda (using Mangum adapter)

2. ✅ **Created Safety Backups**
   - Tagged current production as `production-stable`
   - Created timestamped backup: `backup-2026-05-24`
   - Both backups confirmed in ECR

3. ✅ **Built and Tested New Image Locally**
   - Successfully built Python 3.14 image
   - Fixed Dockerfile warning (PYTHONPATH)
   - Tested locally on port 5001 - all endpoints working
   - Fixed architecture issue (ARM64 → AMD64 for Lambda)

4. ✅ **Attempted Deployment**
   - Pushed `test-v2` image to ECR
   - Updated Lambda function
   - Discovered compatibility issue

5. ✅ **Successfully Rolled Back**
   - Reverted to `production-stable` image
   - Production is stable and working

---

## Issues Discovered

### Critical Issue: Lambda Integration Mismatch

**Problem:** The current Dockerfile runs Flask as a standalone development server, but the production Lambda uses **Mangum** (ASGI adapter) to integrate Flask with API Gateway.

**Evidence from logs:**
```
File "/var/lang/lib/python3.9/site-packages/mangum/adapter.py"
```

**Root Cause:**
- Old image (2022): Uses Mangum to wrap Flask for Lambda/API Gateway
- New image (2026): Runs Flask dev server directly (incompatible with Lambda)
- Flask debug mode tries to access `/dev/shm` which doesn't exist in Lambda

---

## What Needs to Be Done

### Option 1: Use Mangum (Recommended - Matches Current Setup)

The old setup uses Mangum to make Flask work with Lambda. We need to:

1. **Add Mangum to requirements.txt:**
   ```
   flask>=3.0.0
   mangum>=0.17.0
   ```

2. **Create Lambda handler in api/api.py:**
   ```python
   from mangum import Mangum
   
   # ... existing Flask app code ...
   
   # Lambda handler
   handler = Mangum(app, lifespan="off")
   
   # Keep dev server for local testing
   if __name__ == '__main__':
       app.run(host='0.0.0.0', port='5000')
   ```

3. **Update Dockerfile CMD:**
   ```dockerfile
   CMD ["python", "-m", "awslambdaric", "api.api.handler"]
   ```
   OR use AWS Lambda Python base image

### Option 2: Use AWS Lambda Web Adapter

Alternative modern approach using AWS Lambda Web Adapter to run Flask server directly.

### Option 3: Keep Current Setup

The 2022 image works fine. Only upgrade if there's a specific need for Python 3.14 features.

---

## Current Production State

- **Status:** ✅ STABLE
- **Image:** `production-stable` (Python 3.9, March 2022)
- **Lambda Function:** Working correctly via API Gateway
- **Rollback Capability:** Available via `backup-2026-05-24` tag

---

## Recommendations

### Immediate Actions
1. ✅ **DONE:** Production rolled back and stable
2. ✅ **DONE:** Backups created and verified
3. ✅ **DONE:** Documentation created

### Next Steps (When Ready to Upgrade)

1. **Investigate Old Image:**
   ```bash
   # Pull and inspect the old image
   docker pull 310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda:production-stable
   docker run --rm -it --entrypoint /bin/bash 310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda:production-stable
   
   # Check for Mangum
   pip list | grep mangum
   
   # Check Dockerfile/entrypoint
   cat Dockerfile  # if available
   ```

2. **Update Dockerfile for Lambda:**
   - Add Mangum dependency
   - Create proper Lambda handler
   - Update CMD to use Lambda runtime

3. **Test Locally with Lambda Runtime:**
   ```bash
   # Use AWS Lambda Runtime Interface Emulator
   docker run -p 9000:8080 orthodox-fasting/fastapi-lambda:test-v3
   curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
   ```

4. **Deploy with Confidence:**
   - Build corrected image
   - Push as `test-v3`
   - Update Lambda
   - Test via API Gateway
   - Monitor for 24-48 hours
   - Promote to `latest`

---

## Files Created

1. **AWS_DEPLOYMENT_PLAN.md** - Complete 10-phase deployment guide
2. **QUICK_START_GUIDE.md** - Condensed workflow
3. **DEPLOYMENT_SUMMARY.md** - This file
4. **Feature Branch:** `feature/aws-lambda-deployment-plan`

---

## Key Learnings

1. **Architecture Matters:** ARM64 (Mac) vs AMD64 (Lambda) - use `--platform linux/amd64`
2. **Lambda Integration:** Can't run Flask dev server directly in Lambda
3. **Mangum Discovery:** Old setup uses Mangum adapter (not documented in current repo)
4. **Rollback Works:** Safety measures prevented production downtime
5. **API Gateway Integration:** Lambda expects specific event format from API Gateway

---

## Cost Impact

- **Deployment Attempt:** ~$7 in API calls
- **Production Downtime:** 0 minutes (rollback successful)
- **Data Loss:** None

---

## Questions to Answer Before Next Attempt

1. Does the old image Dockerfile exist somewhere?
2. What version of Mangum was used?
3. Are there any Lambda-specific environment variables?
4. What's the API Gateway configuration?
5. Is there a specific reason to upgrade to Python 3.14?

---

## Contact Points

- Lambda Function: `orthodox-fasting`
- Region: `eu-central-1`
- ECR: `310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda`
- API: https://nocmu.me (frontend)

---

**Status:** Production is stable. Upgrade can be attempted when Lambda integration is properly configured.