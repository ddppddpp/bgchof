# Docker Integration Tests

## Overview

The `test_docker_integration.py` file contains comprehensive integration tests that validate the complete Docker build and deployment workflow for the bgchof API.

## What the Tests Cover

1. **Docker Build Process**
   - Builds a fresh Docker image from the Dockerfile
   - Validates successful image creation

2. **Container Deployment**
   - Starts containers with proper port mappings
   - Verifies container health and startup

3. **API Endpoint Testing**
   - Root endpoint (`/`)
   - Fasting message endpoint (`/api/v1/msgForDate`)
   - Tests with and without date parameters
   - Invalid input handling

4. **Data Validation**
   - Correct response formats
   - Expected fasting data for known dates
   - Error message formatting

5. **Environment Configuration**
   - PYTHONPATH environment variable
   - Required files presence
   - Container logs analysis

6. **Performance**
   - Response time validation
   - Startup time monitoring

## Prerequisites

- Docker installed and running
- Python 3.9+
- pytest installed (`pip install pytest`)
- requests library installed (`pip install requests`)

## Running the Tests

### Run all Docker integration tests:
```bash
pytest tests/test_docker_integration.py -v
```

### Run with detailed output:
```bash
pytest tests/test_docker_integration.py -v -s
```

### Run a specific test:
```bash
pytest tests/test_docker_integration.py::TestDockerIntegration::test_root_endpoint_responds -v
```

### Run from project root:
```bash
python -m pytest tests/test_docker_integration.py -v
```

## Test Configuration

The tests use the following configuration:
- **Test Image Name**: `bgchof-test-image`
- **Test Container Name**: `bgchof-test-container`
- **Host Port**: `5001` (to avoid conflicts with other services)
- **Container Port**: `5000` (Flask default)
- **Build Timeout**: 300 seconds (5 minutes)
- **Startup Timeout**: 30 seconds

## Test Workflow

1. **Setup Class** (once before all tests):
   - Builds Docker image from current Dockerfile
   - Tags image as `bgchof-test-image`

2. **Setup Method** (before each test):
   - Starts a new container from the test image
   - Waits for container to be ready
   - Verifies API is responding

3. **Test Execution**:
   - Runs individual test cases
   - Makes HTTP requests to API endpoints
   - Validates responses and behavior

4. **Teardown Method** (after each test):
   - Captures container logs
   - Stops and removes container

5. **Teardown Class** (once after all tests):
   - Removes test image
   - Cleans up all Docker resources

## Expected Test Results

All tests should pass if:
- Dockerfile is correctly configured
- Flask API starts successfully
- PYTHONPATH is set to `/app/src`
- All required files are present in the image
- API endpoints return correct responses
- No Python errors in container logs

## Troubleshooting

### Tests fail with "Container did not become ready"
- Check if port 5001 is already in use
- Verify Docker daemon is running
- Check container logs for startup errors

### Tests fail with "Docker build failed"
- Verify Dockerfile syntax
- Check if all required files exist
- Ensure requirements.txt is valid

### Tests fail with connection errors
- Verify firewall settings
- Check if Docker networking is configured correctly
- Ensure no other service is using port 5001

### Container logs show import errors
- Verify PYTHONPATH is set correctly in Dockerfile
- Check that `context.py` files are present
- Ensure module structure matches import statements

## Continuous Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Docker Integration Tests
  run: |
    pip install pytest requests
    pytest tests/test_docker_integration.py -v
```

## Notes

- Tests automatically clean up Docker resources after completion
- Each test runs in an isolated container
- Tests use port 5001 to avoid conflicts with development servers
- Container logs are captured and displayed on test failure
- Build process is only executed once per test session for efficiency

## Test Coverage

The integration tests cover:
- ✅ Docker image build process
- ✅ Container startup and health
- ✅ API endpoint availability
- ✅ Response format validation
- ✅ Date parameter handling
- ✅ Error handling and messages
- ✅ Environment configuration
- ✅ File system structure
- ✅ Performance characteristics
- ✅ Log output validation

## Maintenance

When updating the Dockerfile or API:
1. Run integration tests locally first
2. Update test expectations if API behavior changes
3. Adjust timeouts if build/startup times change
4. Add new tests for new endpoints or features