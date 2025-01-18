import logging
import sys


def setup_logging(
    log_file="app.log",
    console_log_level=None,
    file_log_level=logging.DEBUG,
):
    if len(logging.getLogger().handlers) == 0:
        root_logger = logging.getLogger()
        root_logger.setLevel(file_log_level)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(file_log_level)
        file_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_format)

        root_logger.addHandler(file_handler)

        if console_log_level:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(console_log_level)
            console_format = logging.Formatter("%(message)s")
            console_handler.setFormatter(console_format)
            root_logger.addHandler(console_handler)

        root_logger.info("Logging setup complete.")
