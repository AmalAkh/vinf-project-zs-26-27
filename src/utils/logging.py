import logging
from typing import Literal

logger = logging.getLogger(__name__)

def log(
    msg: str,
    label: str,
    type: Literal["info", "warning", "error"] = "info"
) -> None:
    message = f"[{label}] {msg}"

    if type == "info":
        logger.info(message)
    elif type == "warning":
        logger.warning(message)
    elif type == "error":
        logger.error(message)
    else:
        raise ValueError(f"Unsupported log type: {type}")