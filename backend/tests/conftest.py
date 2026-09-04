import os

# Ensure JWT_SECRET is set for tests to prevent pydantic Settings validation errors
os.environ["JWT_SECRET"] = "test-secret-for-unit-tests-only-32-bytes!"
