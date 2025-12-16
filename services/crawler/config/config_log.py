import logging
import logging.config
import os
from pathlib import Path

LOGGING_COFIG = {
    "version": 1,
    "disable_existing_loggers": False,  # 防止覆蓋其他套件原本的 log 設定
    "formatters": {
        "basis": {
            "format": "[%(levelname)s] %(asctime)s %(module)s %(message)s",
            "style": "%",  # 這是指上面的 format 用甚麼符號
        }
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "basis", "level": "INFO"},
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "basis",
            "level": "ERROR",
            "filename": r"./logs/log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3,
            "encoding": "utf-8",
        },
    },
    "root": {"level": "INFO", "handlers": ["console", "file"]},
}


def set_up_logging(debug=False):
    log_path = Path(LOGGING_COFIG["handlers"]["file"]["filename"])
    log_dir = log_path.parent

    if not os.path.exists(log_dir):
        log_dir.mkdir(parents=True, exist_ok=True)

    logging.config.dictConfig(LOGGING_COFIG)

    if debug is True:
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        for h in root.handlers:
            h.setLevel(logging.DEBUG)
        root.debug(f"Debug mode enabled. Log path: {log_path.absolute()}")


if __name__ == "__main__":
    set_up_logging()

    logger = logging.getLogger(__name__)

    logger.info("這是一條 Info")  # 會出現在 Console
    logger.error("這是一條 Error")  # 會出現在 Console 和 File
