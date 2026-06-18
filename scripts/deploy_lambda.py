#!/usr/bin/env python3
"""
AWS Lambda Deployment Automation Script

This script automates the deployment of Docker images to AWS Lambda via ECR.
It performs the following operations:
1. Backup current ECR image with timestamped tag
2. Build new Docker image locally
3. Authenticate with AWS ECR
4. Tag and push new image to ECR
5. Update Lambda function to use new image
6. Rollback on failure

Security: Never exposes credentials in logs or output.
Configuration: Reads from environment variables (.env file).
"""

import os
import sys
import json
import subprocess
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Tuple
from pathlib import Path
from dataclasses import dataclass


# Exit codes
EXIT_SUCCESS = 0
EXIT_ENV_ERROR = 1
EXIT_BACKUP_ERROR = 2
EXIT_BUILD_ERROR = 3
EXIT_AUTH_ERROR = 4
EXIT_PUSH_ERROR = 5
EXIT_LAMBDA_UPDATE_ERROR = 6
EXIT_ROLLBACK_ERROR = 7

# ECR authentication constants
ECR_LOGIN_USERNAME = 'AWS'


@dataclass
class DeploymentConfig:
    """Configuration for Lambda deployment."""
    aws_account_id: str
    aws_region: str
    ecr_repository_uri: str
    lambda_function_name: str
    image_tag: str = "latest"
    backup_tag_prefix: str = "backup"
    dockerfile_path: str = "Dockerfile.lambda"
    local_image_name: str = "lambda-deployment"
    
    @classmethod
    def from_env(cls) -> 'DeploymentConfig':
        """Load configuration from environment variables."""
        required_vars = [
            'AWS_ACCOUNT_ID',
            'AWS_REGION',
            'ECR_REPOSITORY_URI',
            'LAMBDA_FUNCTION_NAME'
        ]
        
        missing = [var for var in required_vars if not os.getenv(var) or not os.getenv(var).strip()]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return cls(
            aws_account_id=os.getenv('AWS_ACCOUNT_ID', ''),
            aws_region=os.getenv('AWS_REGION', ''),
            ecr_repository_uri=os.getenv('ECR_REPOSITORY_URI', ''),
            lambda_function_name=os.getenv('LAMBDA_FUNCTION_NAME', ''),
            image_tag=os.getenv('IMAGE_TAG', 'latest'),
            backup_tag_prefix=os.getenv('BACKUP_TAG_PREFIX', 'backup'),
            dockerfile_path=os.getenv('DOCKERFILE_PATH', 'Dockerfile.lambda')
        )


class DeploymentLogger:
    """Secure logging that never exposes credentials."""
    
    def __init__(self, log_file: Optional[str] = None):
        self.logger = logging.getLogger('lambda_deployment')
        self.logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # File handler (optional)
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(console_format)
            self.logger.addHandler(file_handler)
    
    def sanitize_message(self, message: str) -> str:
        """Remove sensitive information from log messages."""
        import re
        
        sanitized = message
        
        # Regex patterns to redact actual sensitive values, not just keywords
        # Pattern format: (keyword)(separator)(value) -> (keyword)(separator)[REDACTED]
        sensitive_value_patterns = [
            # AWS credentials with various separators (=, :, space)
            (r'(AWS_ACCESS_KEY[_ID]*\s*[=:]\s*)([A-Z0-9]+)', r'\1[REDACTED]'),
            (r'(AWS_SECRET[_ACCESS_KEY]*\s*[=:]\s*)([A-Za-z0-9/+=]+)', r'\1[REDACTED]'),
            # Generic patterns for password, secret, token, key, credential
            # Handles compound words (e.g., secret_key) and various separators
            (r'(\w*password\w*\s*[=:]\s*)([^\s]+)', r'\1[REDACTED]', re.IGNORECASE),
            (r'(\w*secret\w*\s*[=:]\s*)([^\s]+)', r'\1[REDACTED]', re.IGNORECASE),
            (r'(\w*token\w*\s*[=:]\s*)([^\s]+)', r'\1[REDACTED]', re.IGNORECASE),
            (r'(\w*key\w*\s*[=:]\s*)([^\s]+)', r'\1[REDACTED]', re.IGNORECASE),
            (r'(\w*credential\w*\s*[=:]\s*)([^\s]+)', r'\1[REDACTED]', re.IGNORECASE),
        ]
        
        for pattern_tuple in sensitive_value_patterns:
            if len(pattern_tuple) == 3:
                pattern, replacement, flags = pattern_tuple
                sanitized = re.sub(pattern, replacement, sanitized, flags=flags)
            else:
                pattern, replacement = pattern_tuple
                sanitized = re.sub(pattern, replacement, sanitized)
        
        # Mask AWS account IDs in ECR URIs (12-digit numbers in ECR context)
        # Pattern: {account-id}.dkr.ecr.{region}.amazonaws.com
        sanitized = re.sub(r'\b(\d{12})\.dkr\.ecr\.([a-z0-9-]+)\.amazonaws\.com',
                          r'[ACCOUNT_ID].dkr.ecr.\2.amazonaws.com', sanitized)
        
        return sanitized
    
    def info(self, message: str):
        self.logger.info(self.sanitize_message(message))
    
    def error(self, message: str):
        self.logger.error(self.sanitize_message(message))
    
    def warning(self, message: str):
        self.logger.warning(self.sanitize_message(message))
    
    def debug(self, message: str):
        self.logger.debug(self.sanitize_message(message))


class CommandExecutor:
    """Execute shell commands with proper error handling."""
    
    def __init__(self, logger: DeploymentLogger, dry_run: bool = False):
        self.logger = logger
        self.dry_run = dry_run
    
    def run(self, command: list, check: bool = True, capture_output: bool = True) -> Tuple[int, str, str]:
        """
        Execute a shell command.
        
        Args:
            command: List of command arguments (e.g., ['aws', 'lambda', 'get-function'])
            check: Whether to check for errors
            capture_output: Whether to capture stdout/stderr
        
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        self.logger.info(f"Executing: {' '.join(command)}")
        
        if self.dry_run:
            self.logger.info("[DRY RUN] Command not executed")
            return (0, "", "")
        
        try:
            result = subprocess.run(
                command,
                shell=False,
                capture_output=capture_output,
                text=True,
                check=False
            )
            
            if result.returncode != 0 and check:
                self.logger.error(f"Command failed with exit code {result.returncode}")
                if result.stderr:
                    self.logger.error(f"Error output: {result.stderr}")
            
            return (result.returncode, result.stdout, result.stderr)
        
        except Exception as e:
            self.logger.error(f"Exception executing command: {str(e)}")
            if check:
                raise
            return (1, "", str(e))


class LambdaDeployer:
    """Main deployment orchestrator."""
    
    def __init__(self, config: DeploymentConfig, logger: DeploymentLogger, 
                 executor: CommandExecutor):
        self.config = config
        self.logger = logger
        self.executor = executor
        self.backup_tag: Optional[str] = None
        self.previous_image_uri: Optional[str] = None
    
    def get_current_lambda_image(self) -> Optional[str]:
        """Get the current Lambda function image URI."""
        self.logger.info(f"Retrieving current image for Lambda function: {self.config.lambda_function_name}")
        
        cmd = [
            'aws', 'lambda', 'get-function',
            '--function-name', self.config.lambda_function_name,
            '--region', self.config.aws_region,
            '--query', 'Code.ImageUri',
            '--output', 'text'
        ]
        
        returncode, stdout, stderr = self.executor.run(cmd)
        
        if returncode != 0:
            self.logger.error("Failed to retrieve current Lambda image")
            return None
        
        image_uri = stdout.strip()
        self.logger.info(f"Current image: {image_uri}")
        return image_uri
    
    def backup_current_image(self) -> bool:
        """Backup the current ECR image with a timestamped tag.
        
        WARNING: Race Condition Limitation
        -----------------------------------
        This method retrieves the current Lambda image URI, then pulls, tags,
        and pushes it. If another deployment occurs between getting the URI and
        completing the backup, the backup might not represent the actual
        pre-deployment state.
        
        Recommendation: Use deployment pipelines (e.g., GitHub Actions, GitLab CI,
        AWS CodePipeline) that serialize deployments to prevent concurrent
        deployments to the same Lambda function. Alternatively, implement external
        locking mechanisms (e.g., DynamoDB conditional writes, S3 object locks).
        """
        self.logger.info("Starting image backup process")
        self.logger.warning(
            "Concurrent deployments may cause backup inconsistencies. "
            "Ensure deployments are serialized via pipeline or locking mechanism."
        )
        
        # Get current Lambda image if not already set
        if not self.previous_image_uri:
            self.previous_image_uri = self.get_current_lambda_image()
        
        if not self.previous_image_uri:
            self.logger.warning("No current image found, skipping backup")
            return True
        
        # Generate backup tag
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
        self.backup_tag = f"{self.config.backup_tag_prefix}-{timestamp}"
        
        self.logger.info(f"Creating backup with tag: {self.backup_tag}")
        
        # Pull current image
        cmd = ['docker', 'pull', self.previous_image_uri]
        returncode, _, _ = self.executor.run(cmd)
        if returncode != 0:
            self.logger.error("Failed to pull current image for backup")
            return False
        
        # Tag for backup
        backup_uri = f"{self.config.ecr_repository_uri}:{self.backup_tag}"
        cmd = ['docker', 'tag', self.previous_image_uri, backup_uri]
        returncode, _, _ = self.executor.run(cmd)
        if returncode != 0:
            self.logger.error("Failed to tag backup image")
            return False
        
        # Push backup
        cmd = ['docker', 'push', backup_uri]
        returncode, _, _ = self.executor.run(cmd)
        if returncode != 0:
            self.logger.error("Failed to push backup image")
            return False
        
        self.logger.info(f"Backup completed successfully: {backup_uri}")
        return True
    
    def build_docker_image(self) -> bool:
        """Build Docker image locally."""
        self.logger.info("Building Docker image")
        
        if not Path(self.config.dockerfile_path).is_file():
            self.logger.error(f"Dockerfile not found: {self.config.dockerfile_path}")
            return False
        
        image_name = f"{self.config.local_image_name}:{self.config.image_tag}"
        cmd = ['docker', 'build', '-f', self.config.dockerfile_path, '-t', image_name, '.']
        
        returncode, _, _ = self.executor.run(cmd, capture_output=False)
        
        if returncode != 0:
            self.logger.error("Docker build failed")
            return False
        
        self.logger.info("Docker image built successfully")
        return True
    
    def authenticate_ecr(self) -> bool:
        """Authenticate Docker with AWS ECR."""
        self.logger.info("Authenticating with AWS ECR")
        
        # Get ECR login password
        get_password_cmd = ['aws', 'ecr', 'get-login-password', '--region', self.config.aws_region]
        returncode, password, stderr = self.executor.run(get_password_cmd)
        
        if returncode != 0:
            self.logger.error("Failed to get ECR login password")
            return False
        
        # Login to Docker with the password
        ecr_registry = f"{self.config.aws_account_id}.dkr.ecr.{self.config.aws_region}.amazonaws.com"
        
        # In dry run mode, skip actual docker login
        if self.executor.dry_run:
            self.logger.info(f"[DRY RUN] Would execute: docker login --username {ECR_LOGIN_USERNAME} --password-stdin {ecr_registry}")
            self.logger.info("ECR authentication successful")
            return True
        
        # Use subprocess directly for stdin input
        try:
            result = subprocess.run(
                ['docker', 'login', '--username', ECR_LOGIN_USERNAME, '--password-stdin', ecr_registry],
                input=password,
                capture_output=True,
                text=True,
                check=False
            )
            returncode = result.returncode
        except Exception as e:
            self.logger.error(f"Docker login failed: {e}")
            return False
        
        if returncode != 0:
            self.logger.error("ECR authentication failed")
            return False
        
        self.logger.info("ECR authentication successful")
        return True
    
    def tag_and_push_image(self) -> bool:
        """Tag and push the new image to ECR."""
        self.logger.info("Tagging and pushing image to ECR")
        
        local_image = f"{self.config.local_image_name}:{self.config.image_tag}"
        remote_image = f"{self.config.ecr_repository_uri}:{self.config.image_tag}"
        
        # Tag image
        cmd = ['docker', 'tag', local_image, remote_image]
        returncode, _, _ = self.executor.run(cmd)
        if returncode != 0:
            self.logger.error("Failed to tag image")
            return False
        
        # Push image
        cmd = ['docker', 'push', remote_image]
        returncode, _, _ = self.executor.run(cmd, capture_output=False)
        if returncode != 0:
            self.logger.error("Failed to push image to ECR")
            return False
        
        self.logger.info(f"Image pushed successfully: {remote_image}")
        return True
    
    def update_lambda_function(self) -> bool:
        """Update Lambda function to use the new image."""
        self.logger.info("Updating Lambda function")
        
        new_image_uri = f"{self.config.ecr_repository_uri}:{self.config.image_tag}"
        
        cmd = [
            'aws', 'lambda', 'update-function-code',
            '--function-name', self.config.lambda_function_name,
            '--image-uri', new_image_uri,
            '--region', self.config.aws_region
        ]
        
        returncode, stdout, _ = self.executor.run(cmd)
        
        if returncode != 0:
            self.logger.error("Failed to update Lambda function")
            return False
        
        self.logger.info("Lambda function updated successfully")
        
        # Wait for update to complete
        self.logger.info("Waiting for Lambda function update to complete...")
        cmd = [
            'aws', 'lambda', 'wait', 'function-updated',
            '--function-name', self.config.lambda_function_name,
            '--region', self.config.aws_region
        ]
        
        returncode, _, _ = self.executor.run(cmd)
        if returncode != 0:
            self.logger.warning("Wait command failed, but update may have succeeded")
        else:
            self.logger.info("Lambda function update completed")
        
        return True
    
    def rollback(self) -> bool:
        """Rollback to the previous image."""
        if not self.previous_image_uri:
            self.logger.error("No previous image URI available for rollback")
            return False
        
        self.logger.warning(f"Rolling back to previous image: {self.previous_image_uri}")
        
        cmd = [
            'aws', 'lambda', 'update-function-code',
            '--function-name', self.config.lambda_function_name,
            '--image-uri', self.previous_image_uri,
            '--region', self.config.aws_region
        ]
        
        returncode, _, _ = self.executor.run(cmd)
        
        if returncode != 0:
            self.logger.error("Rollback failed!")
            return False
        
        self.logger.info("Rollback command executed successfully")
        
        # Wait for rollback to complete
        self.logger.info("Waiting for Lambda function rollback to complete...")
        wait_cmd = [
            'aws', 'lambda', 'wait', 'function-updated',
            '--function-name', self.config.lambda_function_name,
            '--region', self.config.aws_region
        ]
        
        returncode, _, _ = self.executor.run(wait_cmd)
        if returncode != 0:
            self.logger.error("Wait command failed during rollback")
            return False
        
        self.logger.info("Rollback completed successfully")
        return True
    
    def deploy(self) -> int:
        """Execute the full deployment workflow."""
        self.logger.info("=" * 60)
        self.logger.info("Starting Lambda Deployment")
        self.logger.info("=" * 60)
        
        try:
            # Step 1: Backup current image
            if not self.backup_current_image():
                self.logger.error("Backup failed")
                return EXIT_BACKUP_ERROR
            
            # Step 2: Build new image
            if not self.build_docker_image():
                self.logger.error("Build failed")
                return EXIT_BUILD_ERROR
            
            # Step 3: Authenticate with ECR
            if not self.authenticate_ecr():
                self.logger.error("ECR authentication failed")
                return EXIT_AUTH_ERROR
            
            # Step 4: Tag and push image
            if not self.tag_and_push_image():
                self.logger.error("Push to ECR failed")
                return EXIT_PUSH_ERROR
            
            # Step 5: Update Lambda function
            if not self.update_lambda_function():
                self.logger.error("Lambda update failed, attempting rollback...")
                if self.rollback():
                    self.logger.info("Rollback successful")
                    return EXIT_LAMBDA_UPDATE_ERROR
                else:
                    self.logger.error("Rollback failed!")
                    return EXIT_ROLLBACK_ERROR
            
            self.logger.info("=" * 60)
            self.logger.info("Deployment completed successfully!")
            self.logger.info("=" * 60)
            
            if self.backup_tag:
                self.logger.info(f"Backup available at tag: {self.backup_tag}")
            
            return EXIT_SUCCESS
        
        except KeyboardInterrupt:
            self.logger.warning("Deployment interrupted by user")
            return EXIT_ROLLBACK_ERROR
        
        except Exception as e:
            self.logger.error(f"Unexpected error during deployment: {str(e)}")
            return EXIT_ROLLBACK_ERROR


def load_env_file(env_file: str = '.env'):
    """Load environment variables from .env file."""
    env_path = Path(env_file)
    if not env_path.exists():
        return
    
    logger = logging.getLogger(__name__)
    
    try:
        with open(env_path) as f:
            line_number = 0
            for line in f:
                line_number += 1
                line = line.strip()
                if line and not line.startswith('#'):
                    key, _, value = line.partition('=')
                    if key and value:
                        os.environ.setdefault(key.strip(), value.strip())
                    else:
                        logger.warning(f"Malformed line {line_number} in {env_file}: '{line}' - expected KEY=VALUE format")
    except PermissionError as e:
        logger.error(f"Permission denied reading {env_file}: {e}")
        raise
    except IOError as e:
        logger.error(f"Error reading {env_file}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error parsing {env_file}: {e}")
        raise


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Deploy Docker image to AWS Lambda via ECR'
    )
    parser.add_argument(
        '--env-file',
        default='.env',
        help='Path to .env file (default: .env)'
    )
    parser.add_argument(
        '--log-file',
        help='Path to log file (optional)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate deployment without executing commands'
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    load_env_file(args.env_file)
    
    # Initialize logger
    logger = DeploymentLogger(log_file=args.log_file)
    
    try:
        # Load configuration
        config = DeploymentConfig.from_env()
        
        # Initialize executor
        executor = CommandExecutor(logger, dry_run=args.dry_run)
        
        # Create deployer and execute
        deployer = LambdaDeployer(config, logger, executor)
        exit_code = deployer.deploy()
        
        sys.exit(exit_code)
    
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        logger.error("Please check your .env file and ensure all required variables are set")
        sys.exit(EXIT_ENV_ERROR)
    
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(EXIT_ROLLBACK_ERROR)


if __name__ == '__main__':
    main()

# Made with Bob
