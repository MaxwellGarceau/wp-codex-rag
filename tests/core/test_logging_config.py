"""
Unit tests for core/logging_config.py.

This module tests the logging configuration functionality including:
- ColoredFormatter class
- setup_logging function
- get_logger function
- Third-party logger configuration
- Environment-based logging configuration
"""

import logging
import logging.handlers
import sys
from unittest.mock import Mock, patch

from core.logging_config import (
    ColoredFormatter,
    _configure_third_party_loggers,
    get_logger,
    setup_logging,
)


class TestColoredFormatter:
    """Test cases for ColoredFormatter class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.formatter = ColoredFormatter("%(levelname)s: %(message)s")

    def test_colored_formatter_init(self):
        """Test ColoredFormatter initialization."""
        formatter = ColoredFormatter("%(levelname)s: %(message)s")
        assert formatter._fmt == "%(levelname)s: %(message)s"

    def test_colored_formatter_colors(self):
        """Test that ColoredFormatter has correct color codes."""
        assert ColoredFormatter.COLORS["DEBUG"] == "\033[36m"  # Cyan
        assert ColoredFormatter.COLORS["INFO"] == "\033[32m"  # Green
        assert ColoredFormatter.COLORS["WARNING"] == "\033[33m"  # Yellow
        assert ColoredFormatter.COLORS["ERROR"] == "\033[31m"  # Red
        assert ColoredFormatter.COLORS["CRITICAL"] == "\033[35m"  # Magenta
        assert ColoredFormatter.RESET == "\033[0m"

    def test_colored_formatter_format_debug(self):
        """Test ColoredFormatter formatting for DEBUG level."""
        record = logging.LogRecord(
            name="test",
            level=logging.DEBUG,
            pathname="",
            lineno=0,
            msg="Debug message",
            args=(),
            exc_info=None,
        )

        formatted = self.formatter.format(record)

        # Should contain color codes
        assert "\033[36mDEBUG\033[0m" in formatted
        assert "Debug message" in formatted

    def test_colored_formatter_format_info(self):
        """Test ColoredFormatter formatting for INFO level."""
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Info message",
            args=(),
            exc_info=None,
        )

        formatted = self.formatter.format(record)

        # Should contain color codes
        assert "\033[32mINFO\033[0m" in formatted
        assert "Info message" in formatted

    def test_colored_formatter_format_warning(self):
        """Test ColoredFormatter formatting for WARNING level."""
        record = logging.LogRecord(
            name="test",
            level=logging.WARNING,
            pathname="",
            lineno=0,
            msg="Warning message",
            args=(),
            exc_info=None,
        )

        formatted = self.formatter.format(record)

        # Should contain color codes
        assert "\033[33mWARNING\033[0m" in formatted
        assert "Warning message" in formatted

    def test_colored_formatter_format_error(self):
        """Test ColoredFormatter formatting for ERROR level."""
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="Error message",
            args=(),
            exc_info=None,
        )

        formatted = self.formatter.format(record)

        # Should contain color codes
        assert "\033[31mERROR\033[0m" in formatted
        assert "Error message" in formatted

    def test_colored_formatter_format_critical(self):
        """Test ColoredFormatter formatting for CRITICAL level."""
        record = logging.LogRecord(
            name="test",
            level=logging.CRITICAL,
            pathname="",
            lineno=0,
            msg="Critical message",
            args=(),
            exc_info=None,
        )

        formatted = self.formatter.format(record)

        # Should contain color codes
        assert "\033[35mCRITICAL\033[0m" in formatted
        assert "Critical message" in formatted

    def test_colored_formatter_format_unknown_level(self):
        """Test ColoredFormatter formatting for unknown level."""
        record = logging.LogRecord(
            name="test",
            level=25,  # Custom level
            pathname="",
            lineno=0,
            msg="Custom message",
            args=(),
            exc_info=None,
        )
        record.levelname = "CUSTOM"

        formatted = self.formatter.format(record)

        # Should not contain color codes for unknown level
        assert "CUSTOM" in formatted
        assert "\033[" not in formatted
        assert "Custom message" in formatted

    def test_colored_formatter_custom_format(self):
        """Test ColoredFormatter with custom format string."""
        custom_formatter = ColoredFormatter("%(name)s - %(levelname)s: %(message)s")

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Custom format message",
            args=(),
            exc_info=None,
        )

        formatted = custom_formatter.format(record)

        # Should contain color codes and custom format
        assert "\033[32mINFO\033[0m" in formatted
        assert "test.logger" in formatted
        assert "Custom format message" in formatted


class TestSetupLogging:
    """Test cases for setup_logging function."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Clear existing handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()

    def teardown_method(self):
        """Clean up after each test method."""
        # Clear existing handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()

    @patch("core.logging_config.config")
    def test_setup_logging_development_config(self, mock_config):
        """Test setup_logging with development configuration."""
        mock_config.LOG_LEVEL = "INFO"
        mock_config.DEBUG = True
        mock_config.LOG_FORMAT = "%(levelname)s: %(message)s"
        mock_config.LOG_FILE = ""

        setup_logging()

        root_logger = logging.getLogger()

        # Should have console handler
        assert len(root_logger.handlers) == 1
        assert isinstance(root_logger.handlers[0], logging.StreamHandler)
        assert root_logger.handlers[0].stream == sys.stdout

        # Should be DEBUG level due to DEBUG=True
        assert root_logger.level == logging.DEBUG

    @patch("core.logging_config.config")
    def test_setup_logging_production_config(self, mock_config):
        """Test setup_logging with production configuration."""
        mock_config.LOG_LEVEL = "WARNING"
        mock_config.DEBUG = False
        mock_config.LOG_FORMAT = "%(levelname)s: %(message)s"
        mock_config.LOG_FILE = "test.log"

        with patch("pathlib.Path.mkdir") as mock_mkdir:
            with patch("logging.handlers.RotatingFileHandler") as mock_file_handler:
                mock_handler = Mock()
                mock_handler.level = logging.WARNING
                mock_file_handler.return_value = mock_handler

                setup_logging()

                # Should create logs directory
                mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

                # Should create file handler (path is converted to PosixPath)
                from pathlib import Path
                mock_file_handler.assert_called_once_with(
                    Path("test.log"),
                    maxBytes=10 * 1024 * 1024,  # 10MB
                    backupCount=5,
                    encoding="utf-8",
                )

    @patch("core.logging_config.config")
    def test_setup_logging_with_file_handler(self, mock_config):
        """Test setup_logging with file handler configuration."""
        mock_config.LOG_LEVEL = "INFO"
        mock_config.DEBUG = False
        mock_config.LOG_FORMAT = "%(levelname)s: %(message)s"
        mock_config.LOG_FILE = "app.log"

        with patch("pathlib.Path.mkdir"):
            with patch("logging.handlers.RotatingFileHandler") as mock_file_handler:
                mock_handler = Mock()
                mock_handler.level = logging.INFO
                mock_file_handler.return_value = mock_handler

                setup_logging()

                root_logger = logging.getLogger()

                # Should have both console and file handlers
                assert len(root_logger.handlers) == 2

                # Check file handler configuration (path is converted to PosixPath)
                from pathlib import Path
                mock_file_handler.assert_called_once_with(
                    Path("app.log"),
                    maxBytes=10 * 1024 * 1024,
                    backupCount=5,
                    encoding="utf-8",
                )

    @patch("core.logging_config.config")
    def test_setup_logging_without_file_handler(self, mock_config):
        """Test setup_logging without file handler configuration."""
        mock_config.LOG_LEVEL = "INFO"
        mock_config.DEBUG = False
        mock_config.LOG_FORMAT = "%(levelname)s: %(message)s"
        mock_config.LOG_FILE = ""

        setup_logging()

        root_logger = logging.getLogger()

        # Should only have console handler
        assert len(root_logger.handlers) == 1
        assert isinstance(root_logger.handlers[0], logging.StreamHandler)

    @patch("core.logging_config.config")
    def test_setup_logging_debug_override(self, mock_config):
        """Test that DEBUG=True overrides LOG_LEVEL."""
        mock_config.LOG_LEVEL = "WARNING"
        mock_config.DEBUG = True
        mock_config.LOG_FORMAT = "%(levelname)s: %(message)s"
        mock_config.LOG_FILE = ""

        setup_logging()

        root_logger = logging.getLogger()

        # Should be DEBUG level despite LOG_LEVEL=WARNING
        assert root_logger.level == logging.DEBUG

    @patch("core.logging_config.config")
    def test_setup_logging_invalid_log_level(self, mock_config):
        """Test setup_logging with invalid log level."""
        mock_config.LOG_LEVEL = "INVALID"
        mock_config.DEBUG = False
        mock_config.LOG_FORMAT = "%(levelname)s: %(message)s"
        mock_config.LOG_FILE = ""

        setup_logging()

        root_logger = logging.getLogger()

        # Should default to INFO level
        assert root_logger.level == logging.INFO

    @patch("core.logging_config.config")
    def test_setup_logging_clears_existing_handlers(self, mock_config):
        """Test that setup_logging clears existing handlers."""
        mock_config.LOG_LEVEL = "INFO"
        mock_config.DEBUG = False
        mock_config.LOG_FORMAT = "%(levelname)s: %(message)s"
        mock_config.LOG_FILE = ""

        # Add existing handler
        root_logger = logging.getLogger()
        existing_handler = logging.StreamHandler()
        root_logger.addHandler(existing_handler)

        setup_logging()

        # Should have cleared existing handlers and added new one
        assert len(root_logger.handlers) == 1
        assert root_logger.handlers[0] != existing_handler

    @patch("core.logging_config.config")
    def test_setup_logging_formatters(self, mock_config):
        """Test that setup_logging sets correct formatters."""
        mock_config.LOG_LEVEL = "INFO"
        mock_config.DEBUG = False
        mock_config.LOG_FORMAT = "%(levelname)s: %(message)s"
        mock_config.LOG_FILE = ""

        setup_logging()

        root_logger = logging.getLogger()
        console_handler = root_logger.handlers[0]

        # Console handler should use ColoredFormatter
        assert isinstance(console_handler.formatter, ColoredFormatter)
        assert console_handler.formatter._fmt == "%(levelname)s: %(message)s"

    @patch("core.logging_config.config")
    def test_setup_logging_file_formatter(self, mock_config):
        """Test that file handler uses plain formatter."""
        mock_config.LOG_LEVEL = "INFO"
        mock_config.DEBUG = False
        mock_config.LOG_FORMAT = "%(levelname)s: %(message)s"
        mock_config.LOG_FILE = "test.log"

        with patch("pathlib.Path.mkdir"):
            with patch("logging.handlers.RotatingFileHandler") as mock_file_handler:
                mock_handler = Mock()
                mock_handler.level = logging.INFO
                mock_file_handler.return_value = mock_handler

                setup_logging()

                # File handler should use plain formatter (no colors)
                mock_handler.setFormatter.assert_called_once()
                formatter = mock_handler.setFormatter.call_args[0][0]
                assert isinstance(formatter, logging.Formatter)
                assert not isinstance(formatter, ColoredFormatter)


class TestConfigureThirdPartyLoggers:
    """Test cases for _configure_third_party_loggers function."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Clear existing handlers
        for logger_name in [
            "uvicorn.access",
            "uvicorn.error",
            "fastapi",
            "httpx",
            "openai",
            "chromadb",
            "app",
            "core",
        ]:
            logger = logging.getLogger(logger_name)
            logger.handlers.clear()
            logger.setLevel(logging.NOTSET)

    @patch("core.logging_config.config")
    def test_configure_third_party_loggers_default(self, mock_config):
        """Test third-party logger configuration with default settings."""
        mock_config.DEBUG = False

        _configure_third_party_loggers()

        # Check that third-party loggers are configured
        assert logging.getLogger("uvicorn.access").level == logging.WARNING
        assert logging.getLogger("uvicorn.error").level == logging.INFO
        assert logging.getLogger("fastapi").level == logging.INFO
        assert logging.getLogger("httpx").level == logging.WARNING
        assert logging.getLogger("openai").level == logging.INFO
        assert logging.getLogger("chromadb").level == logging.WARNING

    @patch("core.logging_config.config")
    def test_configure_third_party_loggers_debug_mode(self, mock_config):
        """Test third-party logger configuration in debug mode."""
        mock_config.DEBUG = True

        _configure_third_party_loggers()

        # Check that third-party loggers are configured
        assert logging.getLogger("uvicorn.access").level == logging.WARNING
        assert logging.getLogger("uvicorn.error").level == logging.INFO
        assert logging.getLogger("fastapi").level == logging.INFO
        assert logging.getLogger("httpx").level == logging.WARNING
        assert logging.getLogger("openai").level == logging.INFO
        assert logging.getLogger("chromadb").level == logging.WARNING

        # In debug mode, app and core loggers should be DEBUG
        assert logging.getLogger("app").level == logging.DEBUG
        assert logging.getLogger("core").level == logging.DEBUG

    @patch("core.logging_config.config")
    def test_configure_third_party_loggers_non_debug_mode(self, mock_config):
        """Test third-party logger configuration in non-debug mode."""
        mock_config.DEBUG = False

        _configure_third_party_loggers()

        # In non-debug mode, app and core loggers should not be explicitly set
        # (they inherit from root logger)
        app_logger = logging.getLogger("app")
        core_logger = logging.getLogger("core")

        # These should be NOTSET (inherit from parent)
        assert app_logger.level == logging.NOTSET
        assert core_logger.level == logging.NOTSET


class TestGetLogger:
    """Test cases for get_logger function."""

    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a logger instance."""
        logger = get_logger("test.logger")

        assert isinstance(logger, logging.Logger)
        assert logger.name == "test.logger"

    def test_get_logger_different_names(self):
        """Test that get_logger returns different loggers for different names."""
        logger1 = get_logger("test.logger1")
        logger2 = get_logger("test.logger2")

        assert logger1 != logger2
        assert logger1.name == "test.logger1"
        assert logger2.name == "test.logger2"

    def test_get_logger_same_name_returns_same_instance(self):
        """Test that get_logger returns the same instance for the same name."""
        logger1 = get_logger("test.logger")
        logger2 = get_logger("test.logger")

        assert logger1 is logger2

    def test_get_logger_with_module_name(self):
        """Test get_logger with module name (common usage pattern)."""
        logger = get_logger(__name__)

        assert isinstance(logger, logging.Logger)
        assert logger.name == __name__


class TestLoggingConfigIntegration:
    """Integration tests for logging configuration."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Clear existing handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()

    def teardown_method(self):
        """Clean up after each test method."""
        # Clear existing handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()

    @patch("core.logging_config.config")
    def test_full_logging_setup_integration(self, mock_config):
        """Test complete logging setup integration."""
        mock_config.LOG_LEVEL = "INFO"
        mock_config.DEBUG = False
        mock_config.LOG_FORMAT = "%(levelname)s: %(message)s"
        mock_config.LOG_FILE = ""

        # Setup logging with mocked StreamHandler
        with patch("logging.StreamHandler") as mock_stream_handler:
            mock_handler = Mock()
            mock_handler.level = logging.INFO
            mock_stream_handler.return_value = mock_handler
            
            setup_logging()

            # Get a logger
            logger = get_logger("test.integration")

            # Test that logging works
            logger.info("Test message")

            # Should have created a StreamHandler
            mock_stream_handler.assert_called()

    @patch("core.logging_config.config")
    def test_logging_with_file_handler_integration(self, mock_config):
        """Test logging setup with file handler integration."""
        mock_config.LOG_LEVEL = "INFO"
        mock_config.DEBUG = False
        mock_config.LOG_FORMAT = "%(levelname)s: %(message)s"
        mock_config.LOG_FILE = "test.log"

        with patch("pathlib.Path.mkdir"):
            with patch("logging.handlers.RotatingFileHandler") as mock_file_handler:
                mock_handler = Mock()
                mock_handler.level = logging.INFO
                mock_file_handler.return_value = mock_handler

                # Setup logging
                setup_logging()

                # Get a logger
                logger = get_logger("test.file.integration")

                # Test that logging works
                with patch("sys.stdout"):
                    logger.info("Test file message")

                    # Should have called file handler methods
                    mock_handler.setLevel.assert_called()
                    mock_handler.setFormatter.assert_called()

    @patch("core.logging_config.config")
    def test_logging_levels_integration(self, mock_config):
        """Test different logging levels integration."""
        mock_config.LOG_LEVEL = "WARNING"
        mock_config.DEBUG = False
        mock_config.LOG_FORMAT = "%(levelname)s: %(message)s"
        mock_config.LOG_FILE = ""

        with patch("logging.StreamHandler") as mock_stream_handler:
            mock_handler = Mock()
            mock_handler.level = logging.WARNING
            mock_stream_handler.return_value = mock_handler
            
            setup_logging()

            logger = get_logger("test.levels")
            
            # These should not be logged (below WARNING level)
            logger.debug("Debug message")
            logger.info("Info message")

            # These should be logged
            logger.warning("Warning message")
            logger.error("Error message")

            # Should have created StreamHandler
            mock_stream_handler.assert_called()

    def test_logging_configuration_consistency(self):
        """Test that logging configuration is consistent across calls."""
        with patch("core.logging_config.config") as mock_config:
            mock_config.LOG_LEVEL = "INFO"
            mock_config.DEBUG = False
            mock_config.LOG_FORMAT = "%(levelname)s: %(message)s"
            mock_config.LOG_FILE = ""

            # Setup logging multiple times
            setup_logging()
            root_logger1 = logging.getLogger()
            handler_count1 = len(root_logger1.handlers)

            setup_logging()
            root_logger2 = logging.getLogger()
            handler_count2 = len(root_logger2.handlers)

            # Should have same number of handlers (cleared and recreated)
            assert handler_count1 == handler_count2
            assert root_logger1.level == root_logger2.level
