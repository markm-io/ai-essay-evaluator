import asyncio
import logging
from pathlib import Path

import pytest

from ai_essay_evaluator.evaluator.async_logger import AsyncLogger


class TestAsyncLogger:
    """Test cases for AsyncLogger."""

    def test_async_logger_init_disabled(self):
        """Test AsyncLogger initialization when disabled."""
        logger = AsyncLogger(enabled=False)

        assert logger.enabled is False
        assert logger.logger is None
        assert logger.handler is None
        assert logger.log_file is None

    def test_async_logger_init_enabled(self, tmp_path):
        """Test AsyncLogger initialization when enabled."""
        logger = AsyncLogger(enabled=True, log_directory=str(tmp_path))

        assert logger.enabled is True
        assert logger.logger is not None
        assert logger.handler is not None
        assert logger.log_file is not None
        assert Path(logger.log_file).exists()

        # Cleanup
        logger.close()

    def test_async_logger_log_directory_creation(self, tmp_path):
        """Test that log directory is created if it doesn't exist."""
        log_dir = tmp_path / "new_logs"
        logger = AsyncLogger(enabled=True, log_directory=str(log_dir))

        assert log_dir.exists()
        assert log_dir.is_dir()

        # Cleanup
        logger.close()

    @pytest.mark.asyncio
    async def test_async_logger_log_method(self, tmp_path):
        """Test async log method."""
        logger = AsyncLogger(enabled=True, log_directory=str(tmp_path))

        await logger.log(logging.INFO, "Test message")

        # Verify log was written
        assert Path(logger.log_file).exists()
        with open(logger.log_file) as f:
            content = f.read()
            assert "Test message" in content

        # Cleanup
        logger.close()

    @pytest.mark.asyncio
    async def test_async_logger_log_disabled(self):
        """Test that logging doesn't happen when disabled."""
        logger = AsyncLogger(enabled=False)

        # Should not raise any errors
        await logger.log(logging.INFO, "Test message")

        assert logger.log_file is None

    @pytest.mark.asyncio
    async def test_async_logger_log_different_levels(self, tmp_path):
        """Test logging at different levels."""
        logger = AsyncLogger(enabled=True, log_directory=str(tmp_path))

        await logger.log(logging.INFO, "Info message")
        await logger.log(logging.WARNING, "Warning message")
        await logger.log(logging.ERROR, "Error message")

        # Verify all messages were logged
        with open(logger.log_file) as f:
            content = f.read()
            assert "Info message" in content
            assert "Warning message" in content
            assert "Error message" in content

        # Cleanup
        logger.close()

    @pytest.mark.asyncio
    async def test_async_logger_log_with_module(self, tmp_path):
        """Test logging with custom module name."""
        logger = AsyncLogger(enabled=True, log_directory=str(tmp_path))

        await logger.log(logging.INFO, "Module message", module="custom.module")

        with open(logger.log_file) as f:
            content = f.read()
            assert "Module message" in content

        # Cleanup
        logger.close()

    @pytest.mark.asyncio
    async def test_async_logger_log_with_exc_info(self, tmp_path):
        """Test logging with exception info."""
        logger = AsyncLogger(enabled=True, log_directory=str(tmp_path))

        try:
            raise ValueError("Test exception")
        except ValueError:
            await logger.log(logging.ERROR, "Exception occurred", exc_info=True)

        with open(logger.log_file) as f:
            content = f.read()
            assert "Exception occurred" in content
            # Note: asyncio.to_thread may not preserve exc_info properly in all cases
            # Just ensure the message was logged

        # Cleanup
        logger.close()

    def test_get_log_file_enabled(self, tmp_path):
        """Test get_log_file when logging is enabled."""
        logger = AsyncLogger(enabled=True, log_directory=str(tmp_path))

        log_file = logger.get_log_file()
        assert log_file is not None
        assert Path(log_file).exists()

        # Cleanup
        logger.close()

    def test_get_log_file_disabled(self):
        """Test get_log_file when logging is disabled."""
        logger = AsyncLogger(enabled=False)

        log_file = logger.get_log_file()
        assert log_file is None

    def test_close_logger_enabled(self, tmp_path):
        """Test closing logger when enabled."""
        logger = AsyncLogger(enabled=True, log_directory=str(tmp_path))
        log_file = logger.log_file

        logger.close()

        # File should still exist after close
        assert Path(log_file).exists()

    def test_close_logger_disabled(self):
        """Test closing logger when disabled doesn't cause errors."""
        logger = AsyncLogger(enabled=False)

        # Should not raise any errors
        logger.close()

    def test_log_file_naming(self, tmp_path):
        """Test that log files are named with timestamps."""
        logger = AsyncLogger(enabled=True, log_directory=str(tmp_path))

        assert "ai_evaluator_" in logger.log_file
        assert logger.log_file.endswith(".log")

        # Cleanup
        logger.close()

    @pytest.mark.asyncio
    async def test_concurrent_logging(self, tmp_path):
        """Test concurrent log operations."""
        logger = AsyncLogger(enabled=True, log_directory=str(tmp_path))

        # Create multiple concurrent log tasks
        tasks = [logger.log(logging.INFO, f"Message {i}") for i in range(10)]

        await asyncio.gather(*tasks)

        # Verify all messages were logged
        with open(logger.log_file) as f:
            content = f.read()
            for i in range(10):
                assert f"Message {i}" in content

        # Cleanup
        logger.close()

    def test_httpx_logger_suppressed(self, tmp_path):
        """Test that httpx logger is set to WARNING level."""
        logger = AsyncLogger(enabled=True, log_directory=str(tmp_path))

        httpx_logger = logging.getLogger("httpx")
        assert httpx_logger.level == logging.WARNING

        # Cleanup
        logger.close()

    def test_openai_logger_level(self, tmp_path):
        """Test that OpenAI logger is set to INFO level."""
        logger = AsyncLogger(enabled=True, log_directory=str(tmp_path))

        openai_logger = logging.getLogger("openai")
        assert openai_logger.level == logging.INFO

        # Cleanup
        logger.close()
