import logging
import sys

LOG_LEVEL = logging.DEBUG


LOG_TO_CONSOLE = True
# performance critical if set to DEBUG
CONSOLE_LOG_LEVEL = logging.INFO


def setup_logging(log_file="app.log"):
    if len(logging.getLogger().handlers) == 0:
        root_logger = logging.getLogger()
        root_logger.setLevel(LOG_LEVEL)

        # Create handlers
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(CONSOLE_LOG_LEVEL)
        console_format = logging.Formatter("%(message)s")
        console_handler.setFormatter(console_format)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(LOG_LEVEL)
        file_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_format)

        # Add handlers to the root logger
        root_logger.addHandler(file_handler)

        if LOG_TO_CONSOLE:
            root_logger.addHandler(console_handler)

        root_logger.info("Logging setup complete.")
