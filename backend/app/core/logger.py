import logging
import sys
import json
from datetime import datetime


class JsonFormatter(logging.Formatter):

    def format(self, record):
        return json.dumps(
            {
                "time": datetime.now().isoformat(),
                "level": record.levelname,
                "message": record.getMessage(),
                "module": record.module,
                "func": record.funcName,
            },
            ensure_ascii=False)


def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    logger.handlers.clear()
    logger.addHandler(handler)

    return logger
