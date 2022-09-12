import json

from ..constants import INPUT_EVENT, KEYS, SENDERS, SYSTEM_EVENT
from ..events import Event, SystemEvent
from ..log_formatter import get_logger

logger = get_logger()


def parse_event(data):
    try:
        data = json.loads(data)
    except json.decoder.JSONDecodeError:
        logger.warning(f"Malformed JSON received: {data}")
        return None

    if "type" not in data:
        logger.warning(f"No 'type' in data: {data}")
        return None

    if data["type"] == INPUT_EVENT:
        if (
            all(key in data for key in ("key", "sender", "name"))
            and data["key"] in KEYS
            and data["sender"] in SENDERS
            and isinstance(data["name"], str)
        ):
            # TODO proper name validation
            return Event(data["name"], data["sender"], data["key"])
        else:
            logger.warning(f"Malformed Event received: {data}")
            return None
    elif data["type"] == SYSTEM_EVENT:
        if (
            all(key in data for key in ("name", "value", "text", "data"))
            and isinstance(data["name"], str)
            and isinstance(data["text"], str)
        ):
            # TODO proper value validation
            return SystemEvent(
                data["name"], data["value"], data["text"], data["data"]
            )
        else:
            logger.warning(f"Malformed SystemEvent received: {data}")
            return None
    else:
        logger.warning(f"Unknown 'type' in data: '{data['type']}'")
        return None
