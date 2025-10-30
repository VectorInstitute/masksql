"""Tests for logging configuration utilities."""

import sys
from unittest.mock import patch

from loguru import logger

from src.utils import logging as logging_module
from src.utils.logging import configure_logging


class TestConfigureLogging:
    """Test suite for configure_logging function."""

    def test_configure_logging_default_level(self, monkeypatch):
        """Test logging configuration with default INFO level."""
        monkeypatch.delenv("LOG_LEVEL", raising=False)

        with (
            patch.object(logger, "remove") as mock_remove,
            patch.object(logger, "add") as mock_add,
        ):
            configure_logging()

            # Should attempt to remove default handler
            mock_remove.assert_called_once_with(0)

            # Should add new handler with INFO level
            mock_add.assert_called_once()
            call_args = mock_add.call_args
            assert call_args[0][0] == sys.stderr
            assert call_args[1]["level"] == "INFO"
            assert call_args[1]["colorize"] is True
            assert call_args[1]["enqueue"] is True

    def test_configure_logging_custom_level(self, monkeypatch):
        """Test logging configuration with custom LOG_LEVEL."""
        # Patch the module-level LOG_LEVEL variable
        monkeypatch.setattr(logging_module, "LOG_LEVEL", "DEBUG")

        with (
            patch.object(logger, "remove"),
            patch.object(logger, "add") as mock_add,
        ):
            configure_logging()

            # Should add handler with DEBUG level
            call_args = mock_add.call_args
            assert call_args[1]["level"] == "DEBUG"

    def test_configure_logging_error_level(self, monkeypatch):
        """Test logging configuration with ERROR level."""
        # Patch the module-level LOG_LEVEL variable
        monkeypatch.setattr(logging_module, "LOG_LEVEL", "ERROR")

        with patch.object(logger, "remove"), patch.object(logger, "add") as mock_add:
            configure_logging()

            call_args = mock_add.call_args
            assert call_args[1]["level"] == "ERROR"

    def test_configure_logging_warning_level(self, monkeypatch):
        """Test logging configuration with WARNING level."""
        # Patch the module-level LOG_LEVEL variable
        monkeypatch.setattr(logging_module, "LOG_LEVEL", "WARNING")

        with patch.object(logger, "remove"), patch.object(logger, "add") as mock_add:
            configure_logging()

            call_args = mock_add.call_args
            assert call_args[1]["level"] == "WARNING"

    def test_configure_logging_format(self, monkeypatch):
        """Test that logging format includes expected components."""
        monkeypatch.delenv("LOG_LEVEL", raising=False)

        with patch.object(logger, "remove"), patch.object(logger, "add") as mock_add:
            configure_logging()

            call_args = mock_add.call_args
            format_string = call_args[1]["format"]

            # Check format includes time, process ID, level, and message
            assert "{time:HH:mm:ss}" in format_string
            assert "{process.id}" in format_string
            assert "{level}" in format_string
            assert "{message}" in format_string

    def test_configure_logging_suppresses_exceptions(self, monkeypatch):
        """Test that exceptions during handler removal are suppressed."""
        monkeypatch.delenv("LOG_LEVEL", raising=False)

        with (
            patch.object(logger, "remove", side_effect=ValueError("Handler not found")),
            patch.object(logger, "add") as mock_add,
        ):
            # Should not raise exception
            configure_logging()

            # Should still add new handler despite removal error
            mock_add.assert_called_once()

    def test_configure_logging_enqueue_enabled(self, monkeypatch):
        """Test that async enqueueing is enabled for thread safety."""
        monkeypatch.delenv("LOG_LEVEL", raising=False)

        with patch.object(logger, "remove"), patch.object(logger, "add") as mock_add:
            configure_logging()

            call_args = mock_add.call_args
            assert call_args[1]["enqueue"] is True

    def test_configure_logging_outputs_to_stderr(self, monkeypatch):
        """Test that logging outputs to stderr."""
        monkeypatch.delenv("LOG_LEVEL", raising=False)

        with patch.object(logger, "remove"), patch.object(logger, "add") as mock_add:
            configure_logging()

            # First positional argument should be sys.stderr
            assert mock_add.call_args[0][0] == sys.stderr

    def test_configure_logging_colorize_enabled(self, monkeypatch):
        """Test that colorization is enabled."""
        monkeypatch.delenv("LOG_LEVEL", raising=False)

        with patch.object(logger, "remove"), patch.object(logger, "add") as mock_add:
            configure_logging()

            call_args = mock_add.call_args
            assert call_args[1]["colorize"] is True
