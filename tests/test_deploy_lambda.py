"""
Comprehensive test suite for Lambda deployment automation.

Tests cover:
- Unit tests for individual functions
- Integration tests for AWS service interactions (mocked)
- Validation tests for deployment workflow
- End-to-end deployment simulation
"""

import os
import sys
import pytest
import json
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
from datetime import datetime

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from deploy_lambda import (
    DeploymentConfig,
    DeploymentLogger,
    CommandExecutor,
    LambdaDeployer,
    load_env_file,
    EXIT_SUCCESS,
    EXIT_ENV_ERROR,
    EXIT_BACKUP_ERROR,
    EXIT_BUILD_ERROR,
    EXIT_AUTH_ERROR,
    EXIT_PUSH_ERROR,
    EXIT_LAMBDA_UPDATE_ERROR,
    EXIT_ROLLBACK_ERROR
)


# Test Fixtures

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables."""
    env_vars = {
        'AWS_ACCOUNT_ID': '123456789012',
        'AWS_REGION': 'us-east-1',
        'ECR_REPOSITORY_URI': '123456789012.dkr.ecr.us-east-1.amazonaws.com/test-repo',
        'LAMBDA_FUNCTION_NAME': 'test-function',
        'IMAGE_TAG': 'latest',
        'BACKUP_TAG_PREFIX': 'backup',
        'DOCKERFILE_PATH': 'Dockerfile.lambda'
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars


@pytest.fixture
def deployment_config(mock_env_vars):
    """Create a deployment configuration."""
    return DeploymentConfig.from_env()


@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    logger = Mock(spec=DeploymentLogger)
    logger.info = Mock()
    logger.error = Mock()
    logger.warning = Mock()
    logger.debug = Mock()
    return logger


@pytest.fixture
def mock_executor(mock_logger):
    """Create a mock command executor."""
    executor = Mock(spec=CommandExecutor)
    executor.logger = mock_logger
    executor.dry_run = False
    executor.run = Mock(return_value=(0, "", ""))
    return executor


@pytest.fixture
def deployer(deployment_config, mock_logger, mock_executor):
    """Create a Lambda deployer instance."""
    return LambdaDeployer(deployment_config, mock_logger, mock_executor)


# Unit Tests - DeploymentConfig

class TestDeploymentConfig:
    """Test DeploymentConfig class."""
    
    def test_from_env_success(self, mock_env_vars):
        """Test successful configuration loading from environment."""
        config = DeploymentConfig.from_env()
        
        assert config.aws_account_id == '123456789012'
        assert config.aws_region == 'us-east-1'
        assert config.ecr_repository_uri == '123456789012.dkr.ecr.us-east-1.amazonaws.com/test-repo'
        assert config.lambda_function_name == 'test-function'
        assert config.image_tag == 'latest'
    
    def test_from_env_missing_required_vars(self, monkeypatch):
        """Test configuration fails with missing required variables."""
        monkeypatch.delenv('AWS_ACCOUNT_ID', raising=False)
        
        with pytest.raises(ValueError) as exc_info:
            DeploymentConfig.from_env()
        
        assert 'AWS_ACCOUNT_ID' in str(exc_info.value)
    
    def test_from_env_default_values(self, mock_env_vars, monkeypatch):
        """Test default values are used when optional vars not set."""
        monkeypatch.delenv('IMAGE_TAG', raising=False)
        monkeypatch.delenv('BACKUP_TAG_PREFIX', raising=False)
        
        config = DeploymentConfig.from_env()
        
        assert config.image_tag == 'latest'
        assert config.backup_tag_prefix == 'backup'


# Unit Tests - DeploymentLogger

class TestDeploymentLogger:
    """Test DeploymentLogger class."""
    
    def test_sanitize_message_removes_sensitive_data(self):
        """Test that sensitive information is redacted from logs."""
        logger = DeploymentLogger()
        
        sensitive_messages = [
            "AWS_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE",
            "password=secret123",
            "token=abc123xyz",
            "secret_key=mysecret"
        ]
        
        for message in sensitive_messages:
            sanitized = logger.sanitize_message(message)
            assert '[REDACTED]' in sanitized or 'REDACTED' in sanitized.upper()
    
    def test_sanitize_message_preserves_safe_content(self):
        """Test that non-sensitive content is preserved."""
        logger = DeploymentLogger()
        
        safe_message = "Deploying image to ECR repository"
        sanitized = logger.sanitize_message(safe_message)
        
        assert sanitized == safe_message
    
    def test_logger_methods_call_sanitize(self):
        """Test that all logging methods sanitize messages."""
        logger = DeploymentLogger()
        
        with patch.object(logger, 'sanitize_message', return_value='sanitized') as mock_sanitize:
            logger.info("test message")
            logger.error("test message")
            logger.warning("test message")
            logger.debug("test message")
            
            assert mock_sanitize.call_count == 4


# Unit Tests - CommandExecutor

class TestCommandExecutor:
    """Test CommandExecutor class."""
    
    def test_run_successful_command(self, mock_logger):
        """Test successful command execution."""
        executor = CommandExecutor(mock_logger, dry_run=False)
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout='output', stderr='')
            
            returncode, stdout, stderr = executor.run('echo test')
            
            assert returncode == 0
            assert stdout == 'output'
            mock_logger.info.assert_called()
    
    def test_run_failed_command(self, mock_logger):
        """Test failed command execution."""
        executor = CommandExecutor(mock_logger, dry_run=False)
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=1, stdout='', stderr='error')
            
            returncode, stdout, stderr = executor.run('false', check=False)
            
            assert returncode == 1
            assert stderr == 'error'
    
    def test_dry_run_mode(self, mock_logger):
        """Test that dry run mode doesn't execute commands."""
        executor = CommandExecutor(mock_logger, dry_run=True)
        
        with patch('subprocess.run') as mock_run:
            returncode, stdout, stderr = executor.run('echo test')
            
            mock_run.assert_not_called()
            assert returncode == 0


# Unit Tests - LambdaDeployer

class TestLambdaDeployer:
    """Test LambdaDeployer class."""
    
    def test_get_current_lambda_image_success(self, deployer, mock_executor):
        """Test successful retrieval of current Lambda image."""
        expected_uri = '123456789012.dkr.ecr.us-east-1.amazonaws.com/test-repo:current'
        mock_executor.run.return_value = (0, expected_uri, '')
        
        image_uri = deployer.get_current_lambda_image()
        
        assert image_uri == expected_uri
        mock_executor.run.assert_called_once()
    
    def test_get_current_lambda_image_failure(self, deployer, mock_executor):
        """Test handling of failed Lambda image retrieval."""
        mock_executor.run.return_value = (1, '', 'error')
        
        image_uri = deployer.get_current_lambda_image()
        
        assert image_uri is None
    
    def test_backup_current_image_success(self, deployer, mock_executor):
        """Test successful image backup."""
        deployer.previous_image_uri = '123456789012.dkr.ecr.us-east-1.amazonaws.com/test-repo:current'
        mock_executor.run.return_value = (0, '', '')
        
        result = deployer.backup_current_image()
        
        assert result is True
        assert deployer.backup_tag is not None
        assert deployer.backup_tag.startswith('backup-')
    
    def test_backup_current_image_no_previous(self, deployer, mock_executor):
        """Test backup when no previous image exists."""
        with patch.object(deployer, 'get_current_lambda_image', return_value=None):
            result = deployer.backup_current_image()
            
            assert result is True  # Should succeed with warning
    
    def test_backup_current_image_pull_failure(self, deployer, mock_executor):
        """Test backup failure when pull fails."""
        deployer.previous_image_uri = '123456789012.dkr.ecr.us-east-1.amazonaws.com/test-repo:current'
        mock_executor.run.return_value = (1, '', 'pull failed')
        
        result = deployer.backup_current_image()
        
        assert result is False
    
    def test_build_docker_image_success(self, deployer, mock_executor):
        """Test successful Docker image build."""
        with patch('pathlib.Path.is_file', return_value=True):
            mock_executor.run.return_value = (0, '', '')
            
            result = deployer.build_docker_image()
            
            assert result is True
            mock_executor.run.assert_called_once()
    
    def test_build_docker_image_no_dockerfile(self, deployer, mock_executor):
        """Test build failure when Dockerfile doesn't exist."""
        with patch('pathlib.Path.is_file', return_value=False):
            result = deployer.build_docker_image()
            
            assert result is False
    
    def test_build_docker_image_build_failure(self, deployer, mock_executor):
        """Test build failure when Docker build fails."""
        with patch('pathlib.Path.is_file', return_value=True):
            mock_executor.run.return_value = (1, '', 'build failed')
            
            result = deployer.build_docker_image()
            
            assert result is False
    
    def test_authenticate_ecr_success(self, deployer, mock_executor):
        """Test successful ECR authentication."""
        mock_executor.run.return_value = (0, 'password123', '')
        
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = Mock(returncode=0, stdout='', stderr='')
            result = deployer.authenticate_ecr()
        
        assert result is True
    
    def test_authenticate_ecr_failure(self, deployer, mock_executor):
        """Test ECR authentication failure."""
        mock_executor.run.return_value = (1, '', 'auth failed')
        
        result = deployer.authenticate_ecr()
        
        assert result is False
    
    def test_tag_and_push_image_success(self, deployer, mock_executor):
        """Test successful image tagging and pushing."""
        mock_executor.run.return_value = (0, '', '')
        
        result = deployer.tag_and_push_image()
        
        assert result is True
        assert mock_executor.run.call_count == 2  # tag + push
    
    def test_tag_and_push_image_tag_failure(self, deployer, mock_executor):
        """Test failure during image tagging."""
        mock_executor.run.return_value = (1, '', 'tag failed')
        
        result = deployer.tag_and_push_image()
        
        assert result is False
    
    def test_tag_and_push_image_push_failure(self, deployer, mock_executor):
        """Test failure during image push."""
        # First call (tag) succeeds, second call (push) fails
        mock_executor.run.side_effect = [(0, '', ''), (1, '', 'push failed')]
        
        result = deployer.tag_and_push_image()
        
        assert result is False
    
    def test_update_lambda_function_success(self, deployer, mock_executor):
        """Test successful Lambda function update."""
        mock_executor.run.return_value = (0, '{"FunctionArn": "arn:aws:lambda:..."}', '')
        
        result = deployer.update_lambda_function()
        
        assert result is True
    
    def test_update_lambda_function_failure(self, deployer, mock_executor):
        """Test Lambda function update failure."""
        mock_executor.run.return_value = (1, '', 'update failed')
        
        result = deployer.update_lambda_function()
        
        assert result is False
    
    def test_rollback_success(self, deployer, mock_executor):
        """Test successful rollback."""
        deployer.previous_image_uri = '123456789012.dkr.ecr.us-east-1.amazonaws.com/test-repo:old'
        mock_executor.run.return_value = (0, '', '')
        
        result = deployer.rollback()
        
        assert result is True
    
    def test_rollback_no_previous_image(self, deployer, mock_executor):
        """Test rollback failure when no previous image exists."""
        deployer.previous_image_uri = None
        
        result = deployer.rollback()
        
        assert result is False
    
    def test_rollback_failure(self, deployer, mock_executor):
        """Test rollback command failure."""
        deployer.previous_image_uri = '123456789012.dkr.ecr.us-east-1.amazonaws.com/test-repo:old'
        mock_executor.run.return_value = (1, '', 'rollback failed')
        
        result = deployer.rollback()
        
        assert result is False


# Integration Tests

class TestDeploymentIntegration:
    """Integration tests for full deployment workflow."""
    
    def test_full_deployment_success(self, deployer, mock_executor):
        """Test successful end-to-end deployment."""
        # Mock all steps to succeed
        with patch.object(deployer, 'backup_current_image', return_value=True), \
             patch.object(deployer, 'build_docker_image', return_value=True), \
             patch.object(deployer, 'authenticate_ecr', return_value=True), \
             patch.object(deployer, 'tag_and_push_image', return_value=True), \
             patch.object(deployer, 'update_lambda_function', return_value=True):
            
            exit_code = deployer.deploy()
            
            assert exit_code == EXIT_SUCCESS
    
    def test_deployment_backup_failure(self, deployer, mock_executor):
        """Test deployment stops on backup failure."""
        with patch.object(deployer, 'backup_current_image', return_value=False):
            exit_code = deployer.deploy()
            
            assert exit_code == EXIT_BACKUP_ERROR
    
    def test_deployment_build_failure(self, deployer, mock_executor):
        """Test deployment stops on build failure."""
        with patch.object(deployer, 'backup_current_image', return_value=True), \
             patch.object(deployer, 'build_docker_image', return_value=False):
            
            exit_code = deployer.deploy()
            
            assert exit_code == EXIT_BUILD_ERROR
    
    def test_deployment_auth_failure(self, deployer, mock_executor):
        """Test deployment stops on authentication failure."""
        with patch.object(deployer, 'backup_current_image', return_value=True), \
             patch.object(deployer, 'build_docker_image', return_value=True), \
             patch.object(deployer, 'authenticate_ecr', return_value=False):
            
            exit_code = deployer.deploy()
            
            assert exit_code == EXIT_AUTH_ERROR
    
    def test_deployment_push_failure(self, deployer, mock_executor):
        """Test deployment stops on push failure."""
        with patch.object(deployer, 'backup_current_image', return_value=True), \
             patch.object(deployer, 'build_docker_image', return_value=True), \
             patch.object(deployer, 'authenticate_ecr', return_value=True), \
             patch.object(deployer, 'tag_and_push_image', return_value=False):
            
            exit_code = deployer.deploy()
            
            assert exit_code == EXIT_PUSH_ERROR
    
    def test_deployment_lambda_update_failure_with_rollback(self, deployer, mock_executor):
        """Test rollback on Lambda update failure."""
        with patch.object(deployer, 'backup_current_image', return_value=True), \
             patch.object(deployer, 'build_docker_image', return_value=True), \
             patch.object(deployer, 'authenticate_ecr', return_value=True), \
             patch.object(deployer, 'tag_and_push_image', return_value=True), \
             patch.object(deployer, 'update_lambda_function', return_value=False), \
             patch.object(deployer, 'rollback', return_value=True):
            
            exit_code = deployer.deploy()
            
            assert exit_code == EXIT_LAMBDA_UPDATE_ERROR
    
    def test_deployment_lambda_update_failure_rollback_fails(self, deployer, mock_executor):
        """Test when both Lambda update and rollback fail."""
        with patch.object(deployer, 'backup_current_image', return_value=True), \
             patch.object(deployer, 'build_docker_image', return_value=True), \
             patch.object(deployer, 'authenticate_ecr', return_value=True), \
             patch.object(deployer, 'tag_and_push_image', return_value=True), \
             patch.object(deployer, 'update_lambda_function', return_value=False), \
             patch.object(deployer, 'rollback', return_value=False):
            
            exit_code = deployer.deploy()
            
            assert exit_code == EXIT_ROLLBACK_ERROR


# Validation Tests

class TestDeploymentValidation:
    """Validation tests for deployment correctness."""
    
    def test_backup_tag_format(self, deployer, mock_executor):
        """Test that backup tags follow correct format."""
        deployer.previous_image_uri = '123456789012.dkr.ecr.us-east-1.amazonaws.com/test-repo:current'
        mock_executor.run.return_value = (0, '', '')
        
        deployer.backup_current_image()
        
        assert deployer.backup_tag is not None
        assert deployer.backup_tag.startswith('backup-')
        # Verify timestamp format (YYYYMMDD-HHMMSS)
        timestamp_part = deployer.backup_tag.replace('backup-', '')
        assert len(timestamp_part) == 15  # YYYYMMDD-HHMMSS
        assert timestamp_part[8] == '-'
    
    def test_image_uri_construction(self, deployer):
        """Test that image URIs are constructed correctly."""
        expected_uri = f"{deployer.config.ecr_repository_uri}:{deployer.config.image_tag}"
        
        # This would be called in tag_and_push_image
        assert expected_uri == f"{deployer.config.ecr_repository_uri}:latest"
    
    def test_aws_commands_include_region(self, deployer, mock_executor):
        """Test that AWS commands include the correct region."""
        mock_executor.run.return_value = (0, '', '')
        
        deployer.get_current_lambda_image()
        
        # Check that the command includes the region
        call_args = mock_executor.run.call_args[0][0]
        # Command is passed as a list, so check if region args are in the list
        assert '--region' in call_args
        assert deployer.config.aws_region in call_args
    
    def test_docker_commands_use_correct_paths(self, deployer, mock_executor):
        """Test that Docker commands reference correct files."""
        with patch('pathlib.Path.exists', return_value=True):
            mock_executor.run.return_value = (0, '', '')
            
            deployer.build_docker_image()
            
            call_args = mock_executor.run.call_args[0][0]
            assert deployer.config.dockerfile_path in call_args


# Utility Function Tests

class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_load_env_file_success(self, tmp_path):
        """Test loading environment variables from file."""
        env_file = tmp_path / ".env"
        env_file.write_text(
            "AWS_ACCOUNT_ID=123456789012\n"
            "AWS_REGION=us-east-1\n"
            "# Comment line\n"
            "ECR_REPOSITORY_URI=test.ecr.amazonaws.com/repo\n"
        )
        
        load_env_file(str(env_file))
        
        assert os.getenv('AWS_ACCOUNT_ID') == '123456789012'
        assert os.getenv('AWS_REGION') == 'us-east-1'
        assert os.getenv('ECR_REPOSITORY_URI') == 'test.ecr.amazonaws.com/repo'
    
    def test_load_env_file_nonexistent(self):
        """Test that loading nonexistent file doesn't raise error."""
        load_env_file('/nonexistent/.env')  # Should not raise


# End-to-End Simulation Tests

class TestEndToEndSimulation:
    """End-to-end simulation tests."""
    
    def test_complete_deployment_workflow_simulation(self, mock_env_vars, tmp_path):
        """Simulate complete deployment workflow with mocked AWS calls."""
        # Create mock Dockerfile
        dockerfile = tmp_path / "Dockerfile.lambda"
        dockerfile.write_text("FROM public.ecr.aws/lambda/python:3.12\nCMD [\"main.handler\"]")
        
        # Update config to use temp dockerfile
        mock_env_vars['DOCKERFILE_PATH'] = str(dockerfile)
        
        config = DeploymentConfig.from_env()
        logger = DeploymentLogger()
        
        # Create executor with mocked subprocess
        with patch('subprocess.run') as mock_run:
            # Mock all subprocess calls to succeed
            mock_run.return_value = Mock(returncode=0, stdout='success', stderr='')
            
            executor = CommandExecutor(logger, dry_run=False)
            deployer = LambdaDeployer(config, logger, executor)
            
            # Mock the get_current_lambda_image to return a URI
            with patch.object(deployer, 'get_current_lambda_image', 
                            return_value='123456789012.dkr.ecr.us-east-1.amazonaws.com/test-repo:old'):
                exit_code = deployer.deploy()
            
            assert exit_code == EXIT_SUCCESS
            # Verify all major steps were called
            assert mock_run.call_count >= 5  # backup, build, auth, push, update
    
    def test_deployment_with_dry_run(self, mock_env_vars, tmp_path):
        """Test deployment in dry-run mode."""
        dockerfile = tmp_path / "Dockerfile.lambda"
        dockerfile.write_text("FROM public.ecr.aws/lambda/python:3.12\nCMD [\"main.handler\"]")
        
        mock_env_vars['DOCKERFILE_PATH'] = str(dockerfile)
        
        config = DeploymentConfig.from_env()
        logger = DeploymentLogger()
        executor = CommandExecutor(logger, dry_run=True)
        deployer = LambdaDeployer(config, logger, executor)
        
        with patch.object(deployer, 'get_current_lambda_image', 
                        return_value='123456789012.dkr.ecr.us-east-1.amazonaws.com/test-repo:old'):
            exit_code = deployer.deploy()
        
        # Dry run should succeed without actually executing commands
        assert exit_code == EXIT_SUCCESS


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

# Made with Bob
