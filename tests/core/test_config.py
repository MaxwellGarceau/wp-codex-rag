"""
Unit tests for core/config.py.

This module tests the configuration management functionality including:
- Config class initialization and defaults
- Environment-specific config classes (TestConfig, LocalConfig, ProductionConfig)
- get_config function with different environments
- Environment variable handling
"""

import os
from unittest.mock import patch

import pytest

from core.config import Config, LocalConfig, ProductionConfig, TestConfig, get_config


class TestConfigClass:
    """Test cases for Config base class."""

    def test_config_defaults(self):
        """Test that Config class has correct default values."""
        config = Config()

        assert config.ENV == "development"
        assert config.DEBUG is True
        assert config.APP_HOST == "0.0.0.0"
        assert config.APP_PORT == 8000
        # Note: OPENAI_API_KEY may be set from environment, so we test it exists
        assert hasattr(config, "OPENAI_API_KEY")
        assert config.OPENAI_MODEL == "gpt-4o-mini"
        assert config.OPENAI_EMBEDDING_MODEL == "text-embedding-3-small"
        assert config.CHROMA_PERSIST_DIRECTORY == ".chroma"
        assert config.CHROMA_SERVER_HOST == "localhost"
        assert config.CHROMA_SERVER_PORT == 8001
        assert config.RAG_COLLECTION_NAME == "wp_codex_plugin"
        assert config.CORS_ORIGINS == "http://localhost:3000,http://localhost:3001"
        assert config.LOG_LEVEL == "INFO"
        assert (
            config.LOG_FORMAT == "%(levelname)s: (%(asctime)s) (%(name)s) %(message)s"
        )
        assert config.LOG_FILE == ""

    def test_config_with_environment_variables(self):
        """Test Config class with environment variables."""
        with patch.dict(
            os.environ,
            {
                "ENV": "test",
                "DEBUG": "false",
                "APP_HOST": "127.0.0.1",
                "APP_PORT": "9000",
                "OPENAI_API_KEY": "test-key",
                "OPENAI_MODEL": "gpt-4",
                "LOG_LEVEL": "DEBUG",
            },
        ):
            config = Config()

            assert config.ENV == "test"
            assert config.DEBUG is False
            assert config.APP_HOST == "127.0.0.1"
            assert config.APP_PORT == 9000
            assert config.OPENAI_API_KEY == "test-key"
            assert config.OPENAI_MODEL == "gpt-4"
            assert config.LOG_LEVEL == "DEBUG"

    def test_config_env_file_settings(self):
        """Test that Config class has correct env file settings."""
        config = Config()

        assert config.Config.env_file == ".env"
        assert config.Config.env_file_encoding == "utf-8"


class TestTestConfigClass:
    """Test cases for TestConfig class."""

    def test_test_config_inherits_from_config(self):
        """Test that TestConfig inherits from Config."""
        test_config = TestConfig()

        # Should have all the same defaults as Config
        assert test_config.ENV == "development"
        assert test_config.DEBUG is True
        assert test_config.APP_HOST == "0.0.0.0"
        assert test_config.APP_PORT == 8000

    def test_test_config_can_override_values(self):
        """Test that TestConfig can override default values."""
        with patch.dict(
            os.environ, {"ENV": "test", "DEBUG": "false", "APP_PORT": "9000"}
        ):
            test_config = TestConfig()

            assert test_config.ENV == "test"
            assert test_config.DEBUG is False
            assert test_config.APP_PORT == 9000


class TestLocalConfigClass:
    """Test cases for LocalConfig class."""

    def test_local_config_inherits_from_config(self):
        """Test that LocalConfig inherits from Config."""
        local_config = LocalConfig()

        # Should have all the same defaults as Config
        assert local_config.ENV == "development"
        assert local_config.DEBUG is True
        assert local_config.APP_HOST == "0.0.0.0"
        assert local_config.APP_PORT == 8000

    def test_local_config_can_override_values(self):
        """Test that LocalConfig can override default values."""
        with patch.dict(
            os.environ, {"ENV": "local", "DEBUG": "false", "APP_PORT": "9000"}
        ):
            local_config = LocalConfig()

            assert local_config.ENV == "local"
            assert local_config.DEBUG is False
            assert local_config.APP_PORT == 9000


class TestProductionConfigClass:
    """Test cases for ProductionConfig class."""

    def test_production_config_overrides(self):
        """Test that ProductionConfig has correct production overrides."""
        prod_config = ProductionConfig()

        # Should override specific values for production
        assert prod_config.DEBUG is False
        assert (
            prod_config.CORS_ORIGINS
            == "https://yourdomain.com,https://www.yourdomain.com"
        )
        assert prod_config.LOG_LEVEL == "WARNING"
        assert prod_config.LOG_FILE == "app.log"

    def test_production_config_inherits_other_values(self):
        """Test that ProductionConfig inherits other values from Config."""
        prod_config = ProductionConfig()

        # Should inherit other values from Config
        assert prod_config.ENV == "development"  # Default from Config
        assert prod_config.APP_HOST == "0.0.0.0"
        assert prod_config.APP_PORT == 8000
        assert prod_config.OPENAI_MODEL == "gpt-4o-mini"

    def test_production_config_with_environment_variables(self):
        """Test ProductionConfig with environment variables."""
        with patch.dict(
            os.environ,
            {
                "ENV": "prod",
                "APP_HOST": "0.0.0.0",
                "APP_PORT": "80",
                "LOG_LEVEL": "ERROR",
            },
        ):
            prod_config = ProductionConfig()

            assert prod_config.ENV == "prod"
            assert prod_config.APP_HOST == "0.0.0.0"
            assert prod_config.APP_PORT == 80
            assert prod_config.DEBUG is False  # Still overridden
            assert (
                prod_config.LOG_LEVEL == "ERROR"
            )  # Environment variable takes precedence


class TestGetConfig:
    """Test cases for get_config function."""

    def test_get_config_test_environment(self):
        """Test get_config returns TestConfig for test environment."""
        with patch.dict(os.environ, {"ENV": "test"}):
            config = get_config()
            assert isinstance(config, TestConfig)

    def test_get_config_local_environment(self):
        """Test get_config returns LocalConfig for local environment."""
        with patch.dict(os.environ, {"ENV": "local"}):
            config = get_config()
            assert isinstance(config, LocalConfig)

    def test_get_config_prod_environment(self):
        """Test get_config returns ProductionConfig for prod environment."""
        with patch.dict(os.environ, {"ENV": "prod"}):
            config = get_config()
            assert isinstance(config, ProductionConfig)

    def test_get_config_default_environment(self):
        """Test get_config returns LocalConfig when ENV is not set."""
        with patch.dict(os.environ, {}, clear=True):
            config = get_config()
            assert isinstance(config, LocalConfig)

    def test_get_config_unknown_environment(self):
        """Test get_config raises KeyError for unknown environment."""
        with patch.dict(os.environ, {"ENV": "unknown"}):
            with pytest.raises(KeyError):
                get_config()

    def test_get_config_environment_variable_priority(self):
        """Test that environment variables take precedence over defaults."""
        with patch.dict(
            os.environ,
            {"ENV": "test", "DEBUG": "false", "APP_PORT": "9000", "LOG_LEVEL": "DEBUG"},
        ):
            config = get_config()
            assert isinstance(config, TestConfig)
            assert config.DEBUG is False
            assert config.APP_PORT == 9000
            assert config.LOG_LEVEL == "DEBUG"

    def test_get_config_multiple_calls_return_same_type(self):
        """Test that multiple calls to get_config return the same type."""
        with patch.dict(os.environ, {"ENV": "test"}):
            config1 = get_config()
            config2 = get_config()
            assert type(config1) == type(config2)

    def test_get_config_different_environments_return_different_instances(self):
        """Test that different environments return different config instances."""
        with patch.dict(os.environ, {"ENV": "test"}):
            test_config = get_config()

        with patch.dict(os.environ, {"ENV": "local"}):
            local_config = get_config()

        assert test_config is not local_config
        assert isinstance(test_config, TestConfig)
        assert isinstance(local_config, LocalConfig)


class TestConfigIntegration:
    """Integration tests for configuration system."""

    def test_config_chain_inheritance(self):
        """Test the inheritance chain of config classes."""
        # Test that all config classes inherit from Config
        from core.config import (
            LocalConfig as CoreLocalConfig,
        )
        from core.config import (
            ProductionConfig as CoreProductionConfig,
        )
        from core.config import (
            TestConfig as CoreTestConfig,
        )

        assert issubclass(CoreTestConfig, Config)
        assert issubclass(CoreLocalConfig, Config)
        assert issubclass(CoreProductionConfig, Config)

    def test_config_instances_are_config_objects(self):
        """Test that all config instances are Config objects."""
        from core.config import (
            LocalConfig as CoreLocalConfig,
        )
        from core.config import (
            ProductionConfig as CoreProductionConfig,
        )
        from core.config import (
            TestConfig as CoreTestConfig,
        )

        test_config = CoreTestConfig()
        local_config = CoreLocalConfig()
        prod_config = CoreProductionConfig()

        assert isinstance(test_config, Config)
        assert isinstance(local_config, Config)
        assert isinstance(prod_config, Config)

    def test_config_environment_consistency(self):
        """Test that config environment settings are consistent."""
        with patch.dict(os.environ, {"ENV": "test"}):
            config = get_config()
            # The config instance should reflect the environment it was created for
            # Note: The ENV field in the config instance reflects the environment variable,
            # not necessarily the config class type
            assert config.ENV == "test"

    def test_config_validation(self):
        """Test that config values are properly validated by Pydantic."""
        # Test valid values
        config = Config(APP_PORT=8080, CHROMA_SERVER_PORT=8002, DEBUG=False)
        assert config.APP_PORT == 8080
        assert config.CHROMA_SERVER_PORT == 8002
        assert config.DEBUG is False

        # Test invalid values (should raise validation errors)
        with pytest.raises(Exception):  # Pydantic validation error
            Config(APP_PORT="invalid_port")

        with pytest.raises(Exception):  # Pydantic validation error
            Config(DEBUG="invalid_boolean")
