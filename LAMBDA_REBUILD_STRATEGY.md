# Lambda Rebuild Strategy - Correct Approach

## Discovery: How Production Actually Works

### Production Image Analysis (backup-2026-05-24)
```
/var/task/
├── __init__.py
├── main.py
├── requirements.txt
└── templates/

/var/lang/lib/python3.9/site-packages/
├── bgchof.py
├── calculateEasterSunday.py
├── fasting_io.py
├── fasting_status.py
└── bgchof-0.5.10.dist-info/
```

**Key Finding:** bgchof is installed as a Python package from GitHub, NOT copied as local files!

### Production requirements.txt
```
bgchof @ git+https://github.com/ddppddpp/bgchof.git
mangum>=0.11.0, <0.12.0
fastapi>=0.70.1, <0.71.0
uvicorn>=0.15.0, <0.16.0
pydantic>=1.8.2, <1.9.0
Jinja2>=3.0.3, <3.1.0
MarkupSafe>=2.0.1, <2.1.0
```

## Why the New Build Failed

The new Dockerfile.lambda correctly copies only main.py, but the requirements.lambda.txt has updated package versions that may have breaking changes:

**Old (Working):**
- Python 3.9
- mangum 0.11.x
- fastapi 0.70.x
- pydantic 1.8.x

**New (Failed):**
- Python 3.14
- mangum 0.18.x
- fastapi 0.115.x
- pydantic 2.0.x (MAJOR VERSION CHANGE!)

## Root Cause

**Pydantic 2.0 has breaking changes!** The code uses Pydantic 1.x syntax which is incompatible with 2.x.

## Correct Rebuild Strategy

### Option 1: Conservative Update (Recommended)
Keep package versions close to production, only update Python version:

```dockerfile
# requirements.lambda.txt
bgchof @ git+https://github.com/ddppddpp/bgchof.git
mangum>=0.11.0, <0.12.0
fastapi>=0.70.1, <0.80.0
uvicorn>=0.15.0, <0.20.0
pydantic>=1.8.2, <2.0.0  # Stay on v1.x
Jinja2>=3.0.3, <3.2.0
MarkupSafe>=2.0.1, <2.2.0
```

### Option 2: Full Modernization
Update code to be compatible with Pydantic 2.x and latest packages.

**Changes needed in main.py:**
- Update Pydantic model syntax
- Update FastAPI compatibility
- Test all endpoints

## Recommended Deployment Plan

### Phase 1: Conservative Update (Quick Win)
1. Update requirements.lambda.txt to use Pydantic 1.x
2. Keep Python 3.14 base image
3. Test locally
4. Deploy with test-v4 tag
5. Verify in production

### Phase 2: Full Modernization (Later)
1. Create separate branch
2. Update code for Pydantic 2.x
3. Update all dependencies
4. Comprehensive testing
5. Deploy when ready

## Updated Dockerfile.lambda

**Current (Correct):**
```dockerfile
FROM public.ecr.aws/lambda/python:3.14

RUN dnf install -y git && dnf clean all

COPY requirements.lambda.txt ${LAMBDA_TASK_ROOT}/requirements.txt
RUN pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt

COPY src/main.py ${LAMBDA_TASK_ROOT}/
COPY templates/ ${LAMBDA_TASK_ROOT}/templates/

CMD [ "main.handler" ]
```

**This is correct!** The issue was package version incompatibility, not missing files.

## Action Items

1. ✅ Rollback complete - production stable on backup-2026-05-24
2. Update requirements.lambda.txt to use Pydantic 1.x
3. Rebuild with conservative dependencies
4. Test locally with Lambda RIE
5. Deploy with test-v4 tag
6. Verify functionality
7. Promote to production

## Testing Checklist

- [ ] Local Docker build succeeds
- [ ] Lambda RIE test passes
- [ ] Import bgchof works
- [ ] Import calculateEasterSunday works
- [ ] /fastingStatus/date endpoint works
- [ ] /fastingStatus/week endpoint works
- [ ] /fastingStatus/month endpoint works
- [ ] /calculateEasterSunday endpoint works
- [ ] Templates render correctly
- [ ] No import errors in CloudWatch logs

## Key Lessons

1. **Production uses pip install from GitHub** - bgchof is a package, not local files
2. **Dockerfile.lambda was correct** - only main.py needed in /var/task/
3. **Package versions matter** - Pydantic 2.x has breaking changes
4. **Always check production image** - assumptions can be wrong
5. **Conservative updates first** - minimize risk with incremental changes