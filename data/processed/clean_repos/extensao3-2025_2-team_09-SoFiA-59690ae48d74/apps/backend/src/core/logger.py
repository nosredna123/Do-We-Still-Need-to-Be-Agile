import logging
import json
import sys
import os
import datetime

IS_DEV = sys.stdout.isatty() or os.getenv("ENV") == "dev"


class JsonFormatter(logging.Formatter):
    """Outputs machine-readable JSON."""

    def format(self, record):
        log_record = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "payload"):
            log_record["payload"] = record.payload
        return json.dumps(log_record)


class DevFormatter(logging.Formatter):
    """Outputs human-readable colored logs."""

    def format(self, record):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        msg = f"{timestamp} | {record.levelname:<8} | {record.module}:{record.funcName} | {record.getMessage()}"
        if hasattr(record, "payload"):
            payload_pretty = json.dumps(record.payload, indent=2, default=str)
            payload_str = "\n".join(
                [f"    {line}" for line in payload_pretty.splitlines()]
            )
            msg += f"\nPAYLOAD:\n{payload_str}"

        if record.exc_info:
            msg += f"\nEXCEPTION:\n{self.formatException(record.exc_info)}"

        return msg


def setup_logger(name: str = "sofia_backend", level: str = "INFO"):
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        if IS_DEV:
            handler.setFormatter(DevFormatter())
        else:
            handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)

    try:
        logger.setLevel(getattr(logging, level.upper()))
    except AttributeError:
        logger.setLevel(logging.INFO)

    return logger


logger = setup_logger()
