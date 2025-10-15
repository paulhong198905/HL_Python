# common/logging_HL.py

import logging

import colorama

# Initialize colorama for Windows support
colorama.init(autoreset=True)

# ANSI colors (colorama handles Windows translation)
COLORS = {
    "DEBUG": "\033[97m",    # Bright white
    "INFO": "\033[96m",     # Light cyan (easier to read on black)
    "WARNING": "\033[93m",  # Bright yellow
    "ERROR": "\033[91m",    # Bright red
    "CRITICAL": "\033[91m", # Bright red
    "RESET": "\033[0m"
}

SHORT_TAGS = {
    "DEBUG": "DEBG",
    "INFO": "INFO",
    "WARNING": "WARN",
    "ERROR": "ERRO",
    "CRITICAL": "CRIT"
}

class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to console logs with fixed-width tags."""
    def format(self, record):
        tag = SHORT_TAGS.get(record.levelname, record.levelname[:4])
        color = COLORS.get(record.levelname, COLORS["RESET"])
        record.levelname = f"{color}{tag}{COLORS['RESET']}"
        return super().format(record)

def setup_logging(
    log_file="app.log",
    level=logging.DEBUG,
    to_console=True,
    to_file=True
):
    """Setup logging with optional console and file output."""
    logger = logging.getLogger()
    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers.clear()

    # File handler (plain)
    if to_file:
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(level)
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname).4s] %(name)s: %(message)s"
        )
        fh.setFormatter(file_formatter)
        logger.addHandler(fh)

    # Console handler (colored)
    if to_console:
        ch = logging.StreamHandler()
        ch.setLevel(level)
        console_formatter = ColoredFormatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        ch.setFormatter(console_formatter)
        logger.addHandler(ch)

# =======================================
# Quick test if running this file directly
# =======================================
if __name__ == "__main__":
    setup_logging(log_file="test.log", to_console=True, to_file=True)
    logger = logging.getLogger(__name__)

    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    logger.critical("This is a CRITICAL message")
