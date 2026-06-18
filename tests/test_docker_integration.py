"""
Comprehensive Docker integration test for bgchof API.

This test validates the complete Docker build and deployment workflow:
- Builds a fresh Docker image from the current Dockerfile
- Starts a container with appropriate port mappings
- Executes health checks against API endpoints
- Validates response formats and data correctness
- Cleans up test resources
"""
import subprocess
import time
from datetime import date

import pytest
import requests


class TestDockerIntegration:
    """Integration tests for Docker deployment workflow."""

    IMAGE_NAME = "bgchof-test-image"
    CONTAINER_NAME = "bgchof-test-container"
    HOST_PORT = "5001"
    CONTAINER_PORT = "5000"
    BASE_URL = f"http://localhost:{HOST_PORT}"
    BUILD_TIMEOUT = 300  # 5 minutes for build
    STARTUP_TIMEOUT = 30  # 30 seconds for container startup

    @classmethod
    def setup_class(cls):
        """Build Docker image before running tests."""
        print(f"\n🔨 Building Docker image: {cls.IMAGE_NAME}")

        # Build the Docker image
        build_cmd = [
            "docker", "build",
            "-t", cls.IMAGE_NAME,
            "."
        ]

        try:
            result = subprocess.run(
                build_cmd,
                capture_output=True,
                text=True,
                timeout=cls.BUILD_TIMEOUT,
                check=True
            )
            print("✅ Docker image built successfully")
            if result.stdout:
                print(f"Build output: {result.stdout[-500:]}")  # Last 500 chars
        except subprocess.CalledProcessError as e:
            print(f"❌ Docker build failed: {e.stderr}")
            raise
        except subprocess.TimeoutExpired:
            print(f"❌ Docker build timed out after {cls.BUILD_TIMEOUT} seconds")
            raise

    @classmethod
    def teardown_class(cls):
        """Clean up Docker resources after all tests."""
        print("\n🧹 Cleaning up Docker resources")

        # Stop and remove container if it exists
        subprocess.run(
            ["docker", "stop", cls.CONTAINER_NAME],
            capture_output=True,
            timeout=10
        )
        subprocess.run(
            ["docker", "rm", cls.CONTAINER_NAME],
            capture_output=True,
            timeout=10
        )

        # Remove test image
        subprocess.run(
            ["docker", "rmi", cls.IMAGE_NAME],
            capture_output=True,
            timeout=30
        )
        print("✅ Cleanup complete")

    def setup_method(self):
        """Start container before each test."""
        print(f"\n🚀 Starting container: {self.CONTAINER_NAME}")

        # Remove any existing container with the same name
        subprocess.run(
            ["docker", "rm", "-f", self.CONTAINER_NAME],
            capture_output=True
        )

        # Start the container
        run_cmd = [
            "docker", "run",
            "-d",
            "--name", self.CONTAINER_NAME,
            "-p", f"{self.HOST_PORT}:{self.CONTAINER_PORT}",
            self.IMAGE_NAME
        ]

        try:
            result = subprocess.run(
                run_cmd,
                capture_output=True,
                text=True,
                timeout=10,
                check=True
            )
            container_id = result.stdout.strip()
            print(f"✅ Container started: {container_id[:12]}")

            # Wait for container to be ready
            self._wait_for_container_ready()

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start container: {e.stderr}")
            raise

    def teardown_method(self):
        """Stop and remove container after each test."""
        # Get container logs before stopping
        try:
            logs_result = subprocess.run(
                ["docker", "logs", self.CONTAINER_NAME],
                capture_output=True,
                text=True,
                timeout=5
            )
            if logs_result.stdout:
                print(f"\n📋 Container logs:\n{logs_result.stdout[-1000:]}")
        except Exception as e:
            print(f"⚠️  Could not retrieve logs: {e}")

        # Stop and remove container
        subprocess.run(
            ["docker", "stop", self.CONTAINER_NAME],
            capture_output=True,
            timeout=10
        )
        subprocess.run(
            ["docker", "rm", self.CONTAINER_NAME],
            capture_output=True,
            timeout=10
        )

    def _wait_for_container_ready(self):
        """Wait for container to be ready to accept requests."""
        print("⏳ Waiting for container to be ready...")
        start_time = time.time()

        while time.time() - start_time < self.STARTUP_TIMEOUT:
            try:
                # Check if container is still running
                inspect_cmd = [
                    "docker", "inspect",
                    "-f", "{{.State.Running}}",
                    self.CONTAINER_NAME
                ]
                result = subprocess.run(
                    inspect_cmd,
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.stdout.strip() != "true":
                    raise RuntimeError("Container stopped unexpectedly")

                # Try to connect to the API
                response = requests.get(
                    f"{self.BASE_URL}/",
                    timeout=2
                )
                if response.status_code == 200:
                    print(f"✅ Container ready after {time.time() - start_time:.1f}s")
                    return

            except (requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout):
                time.sleep(1)
                continue
            except Exception as e:
                print(f"⚠️  Error during readiness check: {e}")
                time.sleep(1)
                continue

        raise TimeoutError(
            f"Container did not become ready within {self.STARTUP_TIMEOUT} seconds"
        )

    def test_container_is_running(self):
        """Verify container is running and healthy."""
        inspect_cmd = [
            "docker", "inspect",
            "-f", "{{.State.Running}}",
            self.CONTAINER_NAME
        ]
        result = subprocess.run(
            inspect_cmd,
            capture_output=True,
            text=True,
            timeout=5,
            check=True
        )

        assert result.stdout.strip() == "true", "Container should be running"

    def test_root_endpoint_responds(self):
        """Test that root endpoint returns expected HTML content."""
        response = requests.get(f"{self.BASE_URL}/", timeout=5)

        assert response.status_code == 200, "Root endpoint should return 200"
        assert "Bulgarian Christian Orthodox Fasting" in response.text, \
            "Root endpoint should contain project title"
        assert "prototype API" in response.text, \
            "Root endpoint should mention API"

    def test_api_endpoint_without_date_returns_today(self):
        """Test API endpoint without date parameter returns today's fasting info."""
        response = requests.get(
            f"{self.BASE_URL}/api/v1/msgForDate",
            timeout=5
        )

        assert response.status_code == 200, "API should return 200"
        assert "Fasting Diet For" in response.text, \
            "Response should contain fasting diet header"
        assert date.today().isoformat() in response.text, \
            "Response should contain today's date"
        assert "According to the Bulgarian Christian Orthodox norms" in response.text, \
            "Response should contain fasting message"

    def test_api_endpoint_with_valid_date(self):
        """Test API endpoint with valid date parameter."""
        test_date = "2023-01-01"
        response = requests.get(
            f"{self.BASE_URL}/api/v1/msgForDate",
            params={"date": test_date},
            timeout=5
        )

        assert response.status_code == 200, "API should return 200 for valid date"
        assert test_date in response.text, \
            f"Response should contain requested date {test_date}"
        assert "Fasting Diet For" in response.text, \
            "Response should contain fasting diet header"
        assert "According to the Bulgarian Christian Orthodox norms" in response.text, \
            "Response should contain fasting message"

    def test_api_endpoint_with_easter_sunday_2021(self):
        """Test API endpoint with known Easter Sunday date (2021-05-02)."""
        test_date = "2021-05-02"
        response = requests.get(
            f"{self.BASE_URL}/api/v1/msgForDate",
            params={"date": test_date},
            timeout=5
        )

        assert response.status_code == 200, "API should return 200"
        assert test_date in response.text, "Response should contain the date"
        # Easter Sunday should allow all foods (status 6)
        assert "meat" in response.text.lower(), \
            "Easter Sunday should allow meat consumption"

    def test_api_endpoint_with_invalid_date_format(self):
        """Test API endpoint handles invalid date format gracefully."""
        response = requests.get(
            f"{self.BASE_URL}/api/v1/msgForDate",
            params={"date": "invalid-date"},
            timeout=5
        )

        assert response.status_code == 200, "API should return 200 even for errors"
        assert "Value Error" in response.text, \
            "Response should indicate value error"
        assert "yyyy-mm-dd format" in response.text, \
            "Response should mention correct date format"

    def test_api_endpoint_with_multiple_dates(self):
        """Test API endpoint with multiple different dates to verify consistency."""
        test_dates = [
            "2022-04-24",  # Easter Sunday 2022
            "2023-12-25",  # Christmas
            "2024-01-01",  # New Year
        ]

        for test_date in test_dates:
            response = requests.get(
                f"{self.BASE_URL}/api/v1/msgForDate",
                params={"date": test_date},
                timeout=5
            )

            assert response.status_code == 200, \
                f"API should return 200 for date {test_date}"
            assert test_date in response.text, \
                f"Response should contain date {test_date}"
            assert "According to the Bulgarian Christian Orthodox norms" in response.text, \
                f"Response should contain fasting message for {test_date}"

    def test_container_logs_show_successful_startup(self):
        """Verify container logs show successful Flask startup without errors."""
        result = subprocess.run(
            ["docker", "logs", self.CONTAINER_NAME],
            capture_output=True,
            text=True,
            timeout=5,
            check=True
        )

        logs = result.stdout + result.stderr

        # Check for Flask startup indicators
        assert "Running on" in logs or "Serving Flask app" in logs, \
            "Logs should show Flask is running"

        # Check that there are no Python errors
        error_indicators = ["Traceback", "Error:", "Exception:", "Failed"]
        for indicator in error_indicators:
            assert indicator not in logs, \
                f"Logs should not contain '{indicator}'"

    def test_response_content_type_is_html(self):
        """Verify API responses have correct content type."""
        response = requests.get(f"{self.BASE_URL}/", timeout=5)

        assert "text/html" in response.headers.get("Content-Type", ""), \
            "Response should have HTML content type"

    def test_api_performance_response_time(self):
        """Verify API responds within acceptable time limits."""
        start_time = time.time()
        response = requests.get(
            f"{self.BASE_URL}/api/v1/msgForDate",
            params={"date": "2023-01-01"},
            timeout=5
        )
        response_time = time.time() - start_time

        assert response.status_code == 200, "API should return 200"
        assert response_time < 2.0, \
            f"API should respond within 2 seconds, took {response_time:.2f}s"

    def test_container_environment_pythonpath(self):
        """Verify PYTHONPATH environment variable is set correctly in container."""
        exec_cmd = [
            "docker", "exec",
            self.CONTAINER_NAME,
            "printenv", "PYTHONPATH"
        ]

        result = subprocess.run(
            exec_cmd,
            capture_output=True,
            text=True,
            timeout=5,
            check=True
        )

        pythonpath = result.stdout.strip()
        assert "/app/src" in pythonpath, \
            f"PYTHONPATH should contain /app/src, got: {pythonpath}"

    def test_container_has_required_files(self):
        """Verify container has all required application files."""
        required_files = [
            "/app/api/api.py",
            "/app/src/bgchof.py",
            "/app/requirements.txt",
        ]

        for file_path in required_files:
            exec_cmd = [
                "docker", "exec",
                self.CONTAINER_NAME,
                "test", "-f", file_path
            ]

            result = subprocess.run(
                exec_cmd,
                capture_output=True,
                timeout=5
            )

            assert result.returncode == 0, \
                f"Container should have file: {file_path}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

# Made with Bob
