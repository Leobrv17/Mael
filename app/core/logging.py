import logging
from logging.config import dictConfig


def setup_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "formatters": {
                "json": {
                    "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
                }
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                    "level": "INFO",
                }
            },
            "root": {"handlers": ["default"], "level": "INFO"},
        }
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
