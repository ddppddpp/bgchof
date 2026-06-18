#!/bin/bash
# AWS Lambda Deployment Automation Script
# 
# This script provides a convenient wrapper around the Python deployment module.
# It handles environment setup, validation, and execution of the deployment process.
#
# Usage:
#   ./deploy_lambda.sh [OPTIONS]
#
# Options:
#   --dry-run       Simulate deployment without executing commands
#   --log-file FILE Write deployment logs to specified file
#   --env-file FILE Use specified environment file (default: .env)
#   --help          Show this help message
#
# Exit Codes:
#   0 - Success
#   1 - Environment configuration error
#   2 - Backup failure
#   3 - Build failure
#   4 - Authentication failure
#   5 - Push failure
#   6 - Lambda update failure
#   7 - Rollback failure

set -euo pipefail

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default values
ENV_FILE="${SCRIPT_DIR}/.env"
DRY_RUN=""
LOG_FILE=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    echo "============================================================"
    echo "$1"
    echo "============================================================"
    echo ""
}

show_help() {
    cat << EOF
AWS Lambda Deployment Automation Script

Usage: $0 [OPTIONS]

Options:
    --dry-run           Simulate deployment without executing commands
    --log-file FILE     Write deployment logs to specified file
    --env-file FILE     Use specified environment file (default: .env)
    --help              Show this help message

Environment Variables (from .env file):
    AWS_ACCOUNT_ID              AWS account ID (required)
    AWS_REGION                  AWS region (required)
    ECR_REPOSITORY_URI          ECR repository URI (required)
    LAMBDA_FUNCTION_NAME        Lambda function name (required)
    IMAGE_TAG                   Docker image tag (default: latest)
    BACKUP_TAG_PREFIX           Backup tag prefix (default: backup)
    DOCKERFILE_PATH             Path to Dockerfile (default: Dockerfile.lambda)

Exit Codes:
    0 - Success
    1 - Environment configuration error
    2 - Backup failure
    3 - Build failure
    4 - Authentication failure
    5 - Push failure
    6 - Lambda update failure
    7 - Rollback failure

Examples:
    # Normal deployment
    $0

    # Dry run to test without executing
    $0 --dry-run

    # Deploy with custom log file
    $0 --log-file deployment-\$(date +%Y%m%d-%H%M%S).log

    # Use different environment file
    $0 --env-file .env.production

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN="--dry-run"
            shift
            ;;
        --log-file)
            LOG_FILE="--log-file $2"
            shift 2
            ;;
        --env-file)
            ENV_FILE="$2"
            shift 2
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Main execution
print_header "AWS Lambda Deployment Automation"

# Check if .env file exists
if [[ ! -f "$ENV_FILE" ]]; then
    print_error "Environment file not found: $ENV_FILE"
    print_info "Please create $ENV_FILE from .env.example:"
    print_info "  cp .env.example $ENV_FILE"
    print_info "  # Edit $ENV_FILE with your AWS configuration"
    exit 1
fi

print_info "Using environment file: $ENV_FILE"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not found"
    exit 1
fi

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    print_error "Docker is required but not found"
    exit 1
fi

# Check if AWS CLI is available
if ! command -v aws &> /dev/null; then
    print_error "AWS CLI is required but not found"
    print_info "Install AWS CLI: https://aws.amazon.com/cli/"
    exit 1
fi

# Verify Docker is running
if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running"
    print_info "Please start Docker and try again"
    exit 1
fi

# Check if deployment script exists
DEPLOY_SCRIPT="${SCRIPT_DIR}/scripts/deploy_lambda.py"
if [[ ! -f "$DEPLOY_SCRIPT" ]]; then
    print_error "Deployment script not found: $DEPLOY_SCRIPT"
    exit 1
fi

# Make deployment script executable
chmod +x "$DEPLOY_SCRIPT"

print_success "Pre-flight checks passed"
echo ""

# Build command
CMD="python3 $DEPLOY_SCRIPT --env-file $ENV_FILE $DRY_RUN $LOG_FILE"

if [[ -n "$DRY_RUN" ]]; then
    print_warning "Running in DRY RUN mode - no changes will be made"
    echo ""
fi

# Execute deployment
print_info "Starting deployment..."
echo ""

if eval "$CMD"; then
    echo ""
    print_header "Deployment Completed Successfully"
    print_success "Lambda function has been updated with the new image"
    
    if [[ -z "$DRY_RUN" ]]; then
        print_info "You can verify the deployment with:"
        print_info "  aws lambda get-function --function-name <FUNCTION_NAME> --region <REGION>"
        print_info "  aws lambda invoke --function-name <FUNCTION_NAME> response.json"
    fi
    
    exit 0
else
    EXIT_CODE=$?
    echo ""
    print_header "Deployment Failed"
    
    case $EXIT_CODE in
        1)
            print_error "Environment configuration error"
            print_info "Check your .env file and ensure all required variables are set"
            ;;
        2)
            print_error "Backup operation failed"
            print_info "Unable to backup current image"
            ;;
        3)
            print_error "Docker build failed"
            print_info "Check Dockerfile and build logs for errors"
            ;;
        4)
            print_error "ECR authentication failed"
            print_info "Verify AWS credentials and permissions"
            ;;
        5)
            print_error "Image push to ECR failed"
            print_info "Check network connectivity and ECR permissions"
            ;;
        6)
            print_error "Lambda function update failed"
            print_info "Rollback may have been performed"
            ;;
        7)
            print_error "Rollback failed"
            print_info "Manual intervention may be required"
            ;;
        *)
            print_error "Unknown error occurred (exit code: $EXIT_CODE)"
            ;;
    esac
    
    if [[ -n "$LOG_FILE" ]]; then
        print_info "Check log file for details: ${LOG_FILE#--log-file }"
    fi
    
    exit $EXIT_CODE
fi

# Made with Bob
