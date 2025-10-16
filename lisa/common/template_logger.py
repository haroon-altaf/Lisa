from __future__ import annotations

import json
import logging
from pathlib import Path

from concurrent_log_handler import ConcurrentRotatingFileHandler

FOLDER_PATH = Path(__file__).resolve().parent.parent.joinpath("logs")
FILE_PATH = FOLDER_PATH.joinpath("log.log")
ENCODING = "utf-8"
CONSOLE_LEVEL = 10
FILE_LEVEL = 30
CONSOLE_FORMATTER = "%(asctime)s | %(levelname)s | %(module)s | Line %(lineno)d | %(funcName)s | %(message)s"
ROTATION_SIZE = 2 * 1024 * 1024
ROTATION_BACKUPS = 5

if not FOLDER_PATH.exists():
    FOLDER_PATH.mkdir(parents=True)


class JSONFormatter(logging.Formatter):
    """
    Class for specifying JSON logging format.
    """

    def format(self, record) -> str:
        log_record = {
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "filename": record.filename,
            "lineno": record.lineno,
            "funcName": record.funcName,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)


class TemplateLogger:
    """
    Class for generating standard loggers for use in multiple modules.
    """

    def __init__(
        self,
        name: str,
        log_path: str = FILE_PATH,
        encoding: str = ENCODING,
        rotation_size: int = ROTATION_SIZE,
        rotation_backups: int = ROTATION_BACKUPS,
        file_level: int = FILE_LEVEL,
        file_format: logging.Formatter = JSONFormatter(),
        console_level: int = CONSOLE_LEVEL,
        console_format: logging.Formatter = logging.Formatter(CONSOLE_FORMATTER),
    ) -> None:
        self.logger = logging.getLogger(name)
        self.logger.setLevel(10)
        self.logger.propagate = False

        if not self.logger.handlers:
            file_handler = ConcurrentRotatingFileHandler(
                log_path, encoding=encoding, maxBytes=rotation_size, backupCount=rotation_backups
            )
            file_handler.namer = lambda x: x.split(".")[0] + "_backup_" + x.split(".")[-1] + ".log"
            file_handler.setLevel(file_level)
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)

            console_handler = logging.StreamHandler()
            console_handler.setLevel(console_level)
            console_handler.setFormatter(console_format)
            self.logger.addHandler(console_handler)


logger = TemplateLogger(__name__).logger
