from app.config import Settings


def test_test_auth_bypass_enabled_in_test_env():
    # conftest.py sets TEST_AUTH_BYPASS=true for the whole test session
    settings = Settings()
    assert settings.TEST_AUTH_BYPASS is True
