"""Tests for logging configuration utilities."""

from unittest.mock import MagicMock, call, patch

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.utils import logging as logging_module
from src.utils.logging import (
    configure_logging,
    log_error,
    log_info,
    log_pipeline_summary,
    log_stage_complete,
    log_stage_start,
    log_success,
    log_warning,
    reset_stage_timings,
)


class TestConfigureLogging:
    """Test suite for configure_logging function."""

    def test_configure_logging_default_level(self, monkeypatch):
        """Test logging configuration with default INFO level."""
        monkeypatch.delenv("LOG_LEVEL", raising=False)

        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            mock_logger.handlers = []

            configure_logging()

            # Should add handler to root logger
            mock_logger.addHandler.assert_called_once()
            # Check that root logger setLevel was called with INFO
            assert call("INFO") in mock_logger.setLevel.call_args_list

    def test_configure_logging_custom_level(self, monkeypatch):
        """Test logging configuration with custom LOG_LEVEL."""
        monkeypatch.setattr(logging_module, "LOG_LEVEL", "DEBUG")

        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            mock_logger.handlers = []

            configure_logging()

            # Should set logger to DEBUG level
            assert call("DEBUG") in mock_logger.setLevel.call_args_list

    def test_configure_logging_error_level(self, monkeypatch):
        """Test logging configuration with ERROR level."""
        monkeypatch.setattr(logging_module, "LOG_LEVEL", "ERROR")

        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            mock_logger.handlers = []

            configure_logging()

            assert call("ERROR") in mock_logger.setLevel.call_args_list

    def test_configure_logging_warning_level(self, monkeypatch):
        """Test logging configuration with WARNING level."""
        monkeypatch.setattr(logging_module, "LOG_LEVEL", "WARNING")

        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            mock_logger.handlers = []

            configure_logging()

            assert call("WARNING") in mock_logger.setLevel.call_args_list

    def test_configure_logging_removes_existing_handlers(self, monkeypatch):
        """Test that existing handlers are removed before adding new ones."""
        monkeypatch.delenv("LOG_LEVEL", raising=False)

        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_handler1 = MagicMock()
            mock_handler2 = MagicMock()
            mock_logger.handlers = [mock_handler1, mock_handler2]
            mock_get_logger.return_value = mock_logger

            configure_logging()

            # Should remove existing handlers
            assert mock_logger.removeHandler.call_count == 2
            mock_logger.removeHandler.assert_any_call(mock_handler1)
            mock_logger.removeHandler.assert_any_call(mock_handler2)

    def test_configure_logging_adds_rich_handler(self, monkeypatch):
        """Test that RichHandler is added with correct configuration."""
        monkeypatch.delenv("LOG_LEVEL", raising=False)

        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            mock_logger.handlers = []

            configure_logging()

            # Should add a handler
            mock_logger.addHandler.assert_called_once()
            added_handler = mock_logger.addHandler.call_args[0][0]

            # Verify it's a RichHandler by checking its type name
            assert added_handler.__class__.__name__ == "RichHandler"

    def test_configure_logging_formatter(self, monkeypatch):
        """Test that the formatter is configured correctly."""
        monkeypatch.delenv("LOG_LEVEL", raising=False)

        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            mock_logger.handlers = []

            configure_logging()

            # Get the handler that was added
            added_handler = mock_logger.addHandler.call_args[0][0]

            # Check the formatter is minimal
            formatter = added_handler.formatter
            assert formatter._fmt == "%(message)s"


class TestLogError:
    """Test suite for log_error function."""

    def test_log_error_simple_message(self):
        """Test logging a simple error message."""
        with patch.object(Console, "print") as mock_print:
            log_error("Test error message")

            # Should print a Panel
            mock_print.assert_called_once()
            panel = mock_print.call_args[0][0]
            assert isinstance(panel, Panel)
            assert panel.border_style == "red"

    def test_log_error_with_context(self):
        """Test logging an error message with context."""
        with patch.object(Console, "print") as mock_print:
            log_error("Test error", file="test.py", line=42)

            # Should print a Panel with context
            mock_print.assert_called_once()
            panel = mock_print.call_args[0][0]
            assert isinstance(panel, Panel)


class TestLogWarning:
    """Test suite for log_warning function."""

    def test_log_warning_simple_message(self):
        """Test logging a simple warning message."""
        with patch.object(Console, "print") as mock_print:
            log_warning("Test warning message")

            # Should print a Panel
            mock_print.assert_called_once()
            panel = mock_print.call_args[0][0]
            assert isinstance(panel, Panel)
            assert panel.border_style == "yellow"

    def test_log_warning_with_context(self):
        """Test logging a warning message with context."""
        with patch.object(Console, "print") as mock_print:
            log_warning("Deprecated function", function="old_func")

            # Should print a Panel with context
            mock_print.assert_called_once()
            panel = mock_print.call_args[0][0]
            assert isinstance(panel, Panel)


class TestLogSuccess:
    """Test suite for log_success function."""

    def test_log_success_simple_message(self):
        """Test logging a simple success message."""
        with patch.object(Console, "print") as mock_print:
            log_success("Operation completed")

            # Should print a Panel
            mock_print.assert_called_once()
            panel = mock_print.call_args[0][0]
            assert isinstance(panel, Panel)
            assert panel.border_style == "green"

    def test_log_success_with_details(self):
        """Test logging a success message with details."""
        with patch.object(Console, "print") as mock_print:
            log_success("File saved", path="/tmp/file.txt", size=1024)

            # Should print a Panel with details
            mock_print.assert_called_once()
            panel = mock_print.call_args[0][0]
            assert isinstance(panel, Panel)


class TestLogInfo:
    """Test suite for log_info function."""

    def test_log_info_simple_message(self):
        """Test logging a simple info message."""
        with patch.object(Console, "print") as mock_print:
            log_info("Processing data")

            # Should print a Panel
            mock_print.assert_called_once()
            panel = mock_print.call_args[0][0]
            assert isinstance(panel, Panel)
            assert panel.border_style == "blue"

    def test_log_info_with_details(self):
        """Test logging an info message with details."""
        with patch.object(Console, "print") as mock_print:
            log_info("Processing", items=100, status="active")

            # Should print a Panel with details
            mock_print.assert_called_once()
            panel = mock_print.call_args[0][0]
            assert isinstance(panel, Panel)


class TestLogStageStart:
    """Test suite for log_stage_start function."""

    def test_log_stage_start(self):
        """Test logging stage start."""
        with patch.object(Console, "print") as mock_print:
            log_stage_start("TestStage")

            # Should print formatted output
            mock_print.assert_called_once()
            call_args = mock_print.call_args[0][0]
            assert "TestStage" in call_args
            assert "Starting Stage" in call_args


class TestLogStageComplete:
    """Test suite for log_stage_complete function."""

    def test_log_stage_complete_fast(self):
        """Test logging stage completion with fast time (< 1s)."""
        with patch.object(Console, "print") as mock_print:
            log_stage_complete("TestStage", 0.5)

            # Should print formatted output with green timing
            mock_print.assert_called_once()
            call_args = mock_print.call_args[0][0]
            assert "TestStage" in call_args
            assert "Done Stage" in call_args
            assert "0.500s" in call_args

    def test_log_stage_complete_medium(self):
        """Test logging stage completion with medium time (1-10s)."""
        with patch.object(Console, "print") as mock_print:
            log_stage_complete("TestStage", 5.0)

            # Should print formatted output with yellow timing
            mock_print.assert_called_once()
            call_args = mock_print.call_args[0][0]
            assert "TestStage" in call_args
            assert "5.00s" in call_args

    def test_log_stage_complete_slow(self):
        """Test logging stage completion with slow time (> 10s)."""
        with patch.object(Console, "print") as mock_print:
            log_stage_complete("TestStage", 15.5)

            # Should print formatted output with red timing
            mock_print.assert_called_once()
            call_args = mock_print.call_args[0][0]
            assert "TestStage" in call_args
            assert "15.50s" in call_args


class TestResetStageTimings:
    """Test suite for reset_stage_timings function."""

    def test_reset_stage_timings(self):
        """Test resetting stage timings."""
        # Add some timings
        with patch.object(Console, "print"):
            log_stage_complete("Stage1", 1.0)
            log_stage_complete("Stage2", 2.0)

        # Reset timings
        reset_stage_timings()

        # Verify timings are empty by checking summary output
        with patch.object(Console, "print") as mock_print:
            log_pipeline_summary(10.0, 100.0, 150.0)

            # Should have been called multiple times (for table, memory, etc.)
            assert mock_print.call_count > 0


class TestLogPipelineSummary:
    """Test suite for log_pipeline_summary function."""

    def test_log_pipeline_summary_basic(self):
        """Test logging pipeline summary without results."""
        reset_stage_timings()

        with patch.object(Console, "print") as mock_print:
            # Add some stage timings first
            log_stage_complete("Stage1", 1.0)
            log_stage_complete("Stage2", 2.0)

            mock_print.reset_mock()

            # Log summary
            log_pipeline_summary(3.0, 100.0, 150.0)

            # Should print multiple times (table, memory, etc.)
            assert mock_print.call_count >= 2

            # Check that at least one call contains a Table
            has_table = False
            for call_args in mock_print.call_args_list:
                if call_args[0]:  # Check positional args
                    arg = call_args[0][0]
                    if isinstance(arg, Table):
                        has_table = True
                        break
            assert has_table

    def test_log_pipeline_summary_with_results(self):
        """Test logging pipeline summary with results."""
        reset_stage_timings()

        with patch.object(Console, "print") as mock_print:
            # Add some stage timings
            log_stage_complete("Stage1", 1.0)

            mock_print.reset_mock()

            # Log summary with results
            results = {"accuracy": 0.95, "latency": 2.5, "count": 100}
            log_pipeline_summary(3.0, 100.0, 150.0, results)

            # Should print multiple times
            assert mock_print.call_count >= 2
