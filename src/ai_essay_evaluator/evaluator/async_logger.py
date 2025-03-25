# src/ai_essay_evaluator/evaluator/async_logger.py
import asyncio
import logging
import os
from datetime import datetime


class AsyncLogger:
    """Async wrapper for logging that allows concurrent log operations"""

    def __init__(self, enabled=False, log_directory="logs"):
        self.enabled = enabled
        self.log_directory = log_directory
        self.logger = None
        self.handler = None
        self.log_file = None

        if enabled:
            self._setup_logger()

    def _setup_logger(self):
        """Setup the logger with file handler"""
        os.makedirs(self.log_directory, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(self.log_directory, f"ai_evaluator_{timestamp}.log")

        # Create file handler
        self.handler = logging.FileHandler(self.log_file)
        self.handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(self.handler)

        # Set httpx logger to WARNING level to suppress INFO messages
        logging.getLogger("httpx").setLevel(logging.WARNING)
        # Set OpenAI logger to INFO to capture relevant OpenAI errors
        logging.getLogger("openai").setLevel(logging.INFO)

        self.logger = logging.getLogger(__name__)

    async def log(self, level, message, module=None, exc_info=False):
        """Asynchronously log a message"""
        if not self.enabled or not self.logger:
            return

        logger_name = module or __name__
        logger = logging.getLogger(logger_name)

        await asyncio.to_thread(logger.log, level, message, exc_info=exc_info)

    def get_log_file(self) -> str | None:
        """Return the log file path if logging is enabled"""
        return self.log_file if self.enabled else None

    def close(self):
        """Close the log handler"""
        if self.enabled and self.handler:
            self.logger.info("Closing log file")
            self.handler.close()
            root_logger = logging.getLogger()
            root_logger.removeHandler(self.handler)
