import os

os.environ.setdefault("TEST_AUTH_BYPASS", "true")
if os.environ.get("TEST_DATABASE_URL"):
    os.environ["DATABASE_URL"] = os.environ["TEST_DATABASE_URL"]
