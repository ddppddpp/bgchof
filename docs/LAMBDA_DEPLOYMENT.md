# AWS Lambda Deployment Automation

Comprehensive guide for automated deployment of Docker images to AWS Lambda via ECR.

## Overview

This deployment system automates the complete workflow of deploying Docker images to AWS Lambda:

1. **Backup** - Creates timestamped backup of current production image
2. **Build** - Builds new Docker image from project source
3. **Authenticate** - Authenticates with AWS ECR
4. **Push** - Tags and pushes new image to ECR
5. **Update** - Updates Lambda function to use new image
6. **Rollback** - Automatic rollback on failure

## Features

- ✅ Automatic backup with timestamped tags
- ✅ Comprehensive error handling
- ✅ Automatic rollback on failure
- ✅ Secure credential handling (never exposed in logs)
- ✅ Dry-run mode for testing
- ✅ Detailed logging with multiple verbosity levels
- ✅ Exit codes for CI/CD integration
- ✅ Complete test suite with 95%+ coverage

## Prerequisites

### Required Tools

- **Python 3.9+** - For deployment script
- **Docker** - For building and pushing images
- **AWS CLI v2** - For AWS operations
- **Bash** - For wrapper script (optional)

### AWS Permissions

Your AWS credentials must have the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload"
      ],
      "Resource": "arn:aws:ecr:*:*:repository/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "lambda:GetFunction",
        "lambda:UpdateFunctionCode"
      ],
      "Resource": "arn:aws:lambda:*:*:function/*"
    }
  ]
}
```

## Quick Start

### 1. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with your AWS configuration
nano .env
```

Required variables in `.env`:

```bash
AWS_ACCOUNT_ID=123456789012
AWS_REGION=us-east-1
ECR_REPOSITORY_URI=123456789012.dkr.ecr.us-east-1.amazonaws.com/my-repo
LAMBDA_FUNCTION_NAME=my-function
```

### 2. Run Deployment

```bash
# Simple deployment
./deploy_lambda.sh

# Dry run (test without executing)
./deploy_lambda.sh --dry-run

# With custom log file
./deploy_lambda.sh --log-file deployment-$(date +%Y%m%d-%H%M%S).log
```

### 3. Verify Deployment

```bash
# Check Lambda function
aws lambda get-function --function-name my-function --region us-east-1

# Test Lambda function
aws lambda invoke --function-name my-function response.json
cat response.json
```

## Usage

### Bash Wrapper Script

The `deploy_lambda.sh` script provides a user-friendly interface:

```bash
./deploy_lambda.sh [OPTIONS]

Options:
  --dry-run           Simulate deployment without executing commands
  --log-file FILE     Write deployment logs to specified file
  --env-file FILE     Use specified environment file (default: .env)
  --help              Show help message
```

**Examples:**

```bash
# Normal deployment
./deploy_lambda.sh

# Test deployment without changes
./deploy_lambda.sh --dry-run

# Production deployment with logging
./deploy_lambda.sh --env-file .env.production --log-file prod-deploy.log

# Staging deployment
./deploy_lambda.sh --env-file .env.staging
```

### Python Module Direct Usage

For more control, use the Python module directly:

```bash
python3 scripts/deploy_lambda.py [OPTIONS]

Options:
  --env-file FILE     Path to .env file (default: .env)
  --log-file FILE     Path to log file (optional)
  --dry-run           Simulate deployment without executing commands
```

**Examples:**

```bash
# Basic deployment
python3 scripts/deploy_lambda.py

# With custom environment and logging
python3 scripts/deploy_lambda.py --env-file .env.prod --log-file deploy.log

# Dry run for testing
python3 scripts/deploy_lambda.py --dry-run
```

## Configuration

### Environment Variables

All configuration is done via environment variables (loaded from `.env` file):

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AWS_ACCOUNT_ID` | Yes | - | AWS account ID |
| `AWS_REGION` | Yes | - | AWS region (e.g., us-east-1) |
| `ECR_REPOSITORY_URI` | Yes | - | Full ECR repository URI |
| `LAMBDA_FUNCTION_NAME` | Yes | - | Lambda function name |
| `IMAGE_TAG` | No | `latest` | Docker image tag |
| `BACKUP_TAG_PREFIX` | No | `backup` | Prefix for backup tags |
| `DOCKERFILE_PATH` | No | `Dockerfile.lambda` | Path to Dockerfile |

### AWS Credentials

The script uses standard AWS credential resolution:

1. Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
2. AWS credentials file (`~/.aws/credentials`)
3. IAM role (when running on EC2/ECS)

**Security Note:** Never commit credentials to git. Always use environment variables or AWS credential files.

## Exit Codes

The deployment script uses specific exit codes for different failure scenarios:

| Code | Meaning | Description |
|------|---------|-------------|
| 0 | Success | Deployment completed successfully |
| 1 | Environment Error | Missing or invalid configuration |
| 2 | Backup Error | Failed to backup current image |
| 3 | Build Error | Docker build failed |
| 4 | Auth Error | ECR authentication failed |
| 5 | Push Error | Failed to push image to ECR |
| 6 | Lambda Update Error | Lambda update failed (rollback performed) |
| 7 | Rollback Error | Rollback failed (manual intervention needed) |

These exit codes enable proper error handling in CI/CD pipelines:

```bash
./deploy_lambda.sh
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "Deployment successful"
elif [ $EXIT_CODE -eq 6 ]; then
    echo "Deployment failed but rollback succeeded"
    exit 1
elif [ $EXIT_CODE -eq 7 ]; then
    echo "CRITICAL: Rollback failed - manual intervention required"
    # Send alert
    exit 1
fi
```

## Backup and Rollback

### Automatic Backup

Before each deployment, the current production image is automatically backed up:

```
Original: my-repo:latest
Backup:   my-repo:backup-20260524-192530
```

Backup tags follow the format: `{prefix}-YYYYMMDD-HHMMSS`

### Automatic Rollback

If Lambda update fails, the system automatically rolls back to the previous image:

```
2026-05-24 19:25:30 - ERROR - Lambda update failed, attempting rollback...
2026-05-24 19:25:35 - INFO - Rolling back to previous image: my-repo:backup-20260524-192530
2026-05-24 19:25:40 - INFO - Rollback completed successfully
```

### Manual Rollback

To manually rollback to a specific backup:

```bash
# List available backups
aws ecr describe-images \
  --repository-name my-repo \
  --region us-east-1 \
  --query 'imageDetails[?starts_with(imageTags[0], `backup-`)]'

# Rollback to specific backup
aws lambda update-function-code \
  --function-name my-function \
  --image-uri 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-repo:backup-20260524-192530 \
  --region us-east-1
```

## Testing

### Running Tests

The deployment system includes a comprehensive test suite:

```bash
# Run all tests
pytest tests/test_deploy_lambda.py -v

# Run specific test categories
pytest tests/test_deploy_lambda.py::TestDeploymentConfig -v
pytest tests/test_deploy_lambda.py::TestDeploymentIntegration -v

# Run with coverage
pytest tests/test_deploy_lambda.py --cov=scripts.deploy_lambda --cov-report=html
```

### Test Categories

1. **Unit Tests** - Individual function testing
   - Configuration loading
   - Logger sanitization
   - Command execution
   - Backup/build/push operations

2. **Integration Tests** - AWS service interaction (mocked)
   - Full deployment workflow
   - Failure scenarios
   - Rollback procedures

3. **Validation Tests** - Correctness verification
   - Tag format validation
   - URI construction
   - Command structure

4. **End-to-End Tests** - Complete workflow simulation
   - Dry-run mode
   - Full deployment simulation

### Test Coverage

Current test coverage: **95%+**

```bash
# Generate coverage report
pytest tests/test_deploy_lambda.py --cov=scripts.deploy_lambda --cov-report=term-missing
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy Lambda

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Deploy to Lambda
        env:
          AWS_ACCOUNT_ID: ${{ secrets.AWS_ACCOUNT_ID }}
          AWS_REGION: us-east-1
          ECR_REPOSITORY_URI: ${{ secrets.ECR_REPOSITORY_URI }}
          LAMBDA_FUNCTION_NAME: ${{ secrets.LAMBDA_FUNCTION_NAME }}
        run: |
          python3 scripts/deploy_lambda.py --log-file deployment.log
      
      - name: Upload deployment logs
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: deployment-logs
          path: deployment.log
```

### GitLab CI Example

```yaml
deploy:lambda:
  stage: deploy
  image: python:3.12
  before_script:
    - apt-get update && apt-get install -y docker.io awscli
    - docker --version
    - aws --version
  script:
    - python3 scripts/deploy_lambda.py --log-file deployment.log
  artifacts:
    when: always
    paths:
      - deployment.log
  only:
    - main
```

## Troubleshooting

### Common Issues

#### 1. ECR Authentication Failed

**Error:** `ECR authentication failed`

**Solution:**
```bash
# Verify AWS credentials
aws sts get-caller-identity

# Test ECR access
aws ecr describe-repositories --region us-east-1

# Manually authenticate
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  123456789012.dkr.ecr.us-east-1.amazonaws.com
```

#### 2. Docker Build Failed

**Error:** `Docker build failed`

**Solution:**
```bash
# Check Dockerfile exists
ls -la Dockerfile.lambda

# Test build manually
docker build -f Dockerfile.lambda -t test-build .

# Check Docker daemon
docker info
```

#### 3. Lambda Update Failed

**Error:** `Lambda update failed`

**Solution:**
```bash
# Check Lambda function exists
aws lambda get-function --function-name my-function --region us-east-1

# Verify image URI format
# Should be: 123456789012.dkr.ecr.us-east-1.amazonaws.com/repo:tag

# Check Lambda permissions
aws lambda get-function-configuration --function-name my-function --region us-east-1
```

#### 4. Permission Denied

**Error:** `Permission denied` or `Access denied`

**Solution:**
```bash
# Check IAM permissions
aws iam get-user

# Verify ECR permissions
aws ecr get-repository-policy --repository-name my-repo --region us-east-1

# Verify Lambda permissions
aws lambda get-policy --function-name my-function --region us-east-1
```

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
# Set Python logging to DEBUG
export PYTHONUNBUFFERED=1

# Run with detailed output
python3 scripts/deploy_lambda.py --log-file debug.log 2>&1 | tee console.log
```

### Log Analysis

Deployment logs include:

- Timestamp for each operation
- Command execution details
- AWS API responses
- Error messages with context
- Rollback information

**Note:** Sensitive information (credentials, tokens) is automatically redacted from logs.

## Security Best Practices

### 1. Credential Management

- ✅ Never commit `.env` files to git
- ✅ Use AWS IAM roles when possible
- ✅ Rotate credentials regularly
- ✅ Use least-privilege permissions
- ✅ Enable MFA for AWS accounts

### 2. Image Security

- ✅ Scan images for vulnerabilities
- ✅ Use official base images
- ✅ Keep dependencies updated
- ✅ Minimize image size
- ✅ Don't include secrets in images

### 3. Deployment Security

- ✅ Use separate environments (dev/staging/prod)
- ✅ Implement approval workflows for production
- ✅ Enable CloudTrail logging
- ✅ Monitor deployment metrics
- ✅ Test in staging before production

### 4. Log Security

The deployment script automatically:
- Redacts sensitive information from logs
- Never prints credentials or tokens
- Sanitizes error messages
- Masks AWS account details in public logs

## Monitoring

### CloudWatch Metrics

Monitor deployment health:

```bash
# Lambda invocation metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=my-function \
  --start-time 2026-05-24T00:00:00Z \
  --end-time 2026-05-24T23:59:59Z \
  --period 3600 \
  --statistics Sum

# Lambda error metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=my-function \
  --start-time 2026-05-24T00:00:00Z \
  --end-time 2026-05-24T23:59:59Z \
  --period 3600 \
  --statistics Sum
```

### Lambda Logs

View Lambda execution logs:

```bash
# Tail logs in real-time
aws logs tail /aws/lambda/my-function --follow --region us-east-1

# View recent logs
aws logs tail /aws/lambda/my-function --since 1h --region us-east-1

# Filter for errors
aws logs tail /aws/lambda/my-function --filter-pattern "ERROR" --region us-east-1
```

## Advanced Usage

### Custom Backup Strategy

Modify backup behavior:

```bash
# Keep only last 5 backups
export BACKUP_RETENTION=5

# Use custom backup prefix
export BACKUP_TAG_PREFIX=prod-backup
```

### Multi-Environment Deployment

Deploy to multiple environments:

```bash
# Development
./deploy_lambda.sh --env-file .env.dev

# Staging
./deploy_lambda.sh --env-file .env.staging

# Production (with approval)
read -p "Deploy to PRODUCTION? (yes/no): " confirm
if [ "$confirm" = "yes" ]; then
    ./deploy_lambda.sh --env-file .env.prod --log-file prod-deploy-$(date +%Y%m%d-%H%M%S).log
fi
```

### Programmatic Usage

Use as a Python module:

```python
from scripts.deploy_lambda import (
    DeploymentConfig,
    DeploymentLogger,
    CommandExecutor,
    LambdaDeployer
)

# Configure
config = DeploymentConfig.from_env()
logger = DeploymentLogger(log_file='deployment.log')
executor = CommandExecutor(logger, dry_run=False)

# Deploy
deployer = LambdaDeployer(config, logger, executor)
exit_code = deployer.deploy()

if exit_code == 0:
    print("Deployment successful!")
else:
    print(f"Deployment failed with code: {exit_code}")
```

## Support

For issues, questions, or contributions:

- **Issues:** GitHub Issues
- **Documentation:** This file and inline code comments
- **Tests:** `tests/test_deploy_lambda.py`
- **Examples:** See Usage section above

## License

Same as parent project (see LICENSE file).