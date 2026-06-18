# Lambda Deployment Status - 2026-05-24

## Current Status: PAUSED - Awaiting GitHub Fix

### Production Status
✅ **Production is STABLE** - Rolled back to `backup-2026-05-24` image
- Image: `310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda:backup-2026-05-24`
- Python: 3.9
- Working correctly

## Root Cause Analysis Complete

### Issue #1: Pydantic Version Incompatibility
- **Problem:** Attempted upgrade to Pydantic 2.x has breaking changes
- **Solution:** Use Pydantic 1.x (conservative approach)
- **Status:** ✅ Fixed in requirements.lambda.txt

### Issue #2: Python 3.14 Incompatibility
- **Problem:** Mangum 0.11.0 uses `cgi` module (removed in Python 3.13+)
- **Solution:** Use Python 3.12 instead of 3.14
- **Status:** ✅ Fixed in Dockerfile.lambda

### Issue #3: GitHub Repo setup.py Bug (CRITICAL)
- **Problem:** setup.py lists wrong module names
  - Lists: `fastingIO`, `fastingStatus` (camelCase)
  - Actual files: `fasting_io.py`, `fasting_status.py` (snake_case)
- **Result:** pip install from GitHub is missing critical modules
- **Solution:** Fix setup.py on GitHub
- **Status:** ⏸️ **WAITING FOR MANUAL FIX**

## Files Modified Locally

### 1. setup.py
```python
# CHANGED FROM:
py_modules=[
    "bgchof",
    "calculateEasterSunday",
    "fastingIO",        # ❌ Wrong
    "fastingStatus",    # ❌ Wrong
    "generateCalendar",
],

# CHANGED TO:
py_modules=[
    "bgchof",
    "calculateEasterSunday",
    "fasting_io",       # ✅ Correct
    "fasting_status",   # ✅ Correct
    "generateCalendar",
],
```

### 2. Dockerfile.lambda
```dockerfile
# Changed from Python 3.14 to 3.12
FROM public.ecr.aws/lambda/python:3.12
```

### 3. requirements.lambda.txt
```
# Conservative package versions (Pydantic 1.x)
bgchof @ git+https://github.com/ddppddpp/bgchof.git
mangum>=0.11.0, <0.12.0
fastapi>=0.70.1, <0.80.0
uvicorn>=0.15.0, <0.20.0
pydantic>=1.8.2, <2.0.0
Jinja2>=3.0.3, <3.2.0
MarkupSafe>=2.0.1, <2.2.0
```

## Next Steps (After GitHub Fix)

1. **Push setup.py fix to GitHub**
   - Commit the setup.py changes
   - Push to main branch
   - Verify the commit is live

2. **Rebuild and test**
   ```bash
   docker build -f Dockerfile.lambda -t orthodox-fasting-lambda:test-v4 --platform linux/amd64 .
   docker run -d -p 9000:8080 --name lambda-test-v4 orthodox-fasting-lambda:test-v4
   curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
     -d '{"rawPath": "/fastingStatus/date", "requestContext": {"http": {"method": "GET"}}, "queryStringParameters": {}}'
   ```

3. **Push to ECR**
   ```bash
   aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 310391119521.dkr.ecr.eu-central-1.amazonaws.com
   docker tag orthodox-fasting-lambda:test-v4 310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda:test-v4
   docker push 310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda:test-v4
   ```

4. **Update Lambda function**
   ```bash
   aws lambda update-function-code \
     --function-name orthodox-fasting \
     --image-uri 310391119521.dkr.ecr.eu-central-1.amazonaws.com/orthodox-fasting/fastapi-lambda:test-v4 \
     --region eu-central-1
   ```

5. **Verify and promote**
   - Test via API Gateway
   - Check CloudWatch logs
   - If successful, tag as latest

## Comparison: Production vs New

| Aspect | Production (backup-2026-05-24) | New (test-v4) |
|--------|-------------------------------|---------------|
| Python | 3.9 | 3.12 |
| Pydantic | 1.8.x | 1.10.x |
| FastAPI | 0.70.x | 0.79.x |
| Mangum | 0.11.x | 0.11.x |
| bgchof | 0.5.10 (camelCase modules) | 0.6.0 (snake_case modules) |
| Status | ✅ Working | ⏸️ Waiting for GitHub fix |

## Documentation Created

1. `LAMBDA_REBUILD_STRATEGY.md` - Complete deployment strategy
2. `internal-monologue/2026-05-24_lambda-failure-analysis.md` - Initial analysis
3. `DEPLOYMENT_STATUS.md` - This file (current status)

## Key Learnings

1. **Always examine production images** - Don't assume structure
2. **Package versions matter** - Major version jumps have breaking changes
3. **Python version compatibility** - Check deprecated modules
4. **setup.py accuracy is critical** - Wrong module names = missing files
5. **Test locally first** - Lambda RIE catches issues early