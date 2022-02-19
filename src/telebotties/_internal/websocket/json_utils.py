import json

from ..constants import KEYS, ORIGINS, SENDERS
from ..log_formatter import get_logger

logger = get_logger()


def encode_message(key, sender, origin, name):
    assert key in KEYS
    assert sender in SENDERS
    assert origin in ORIGINS
    assert isinstance(name, str)
    # TODO proper name validation

    return json.dumps(
        {
            "key": key,
            "sender": sender,
            "origin": origin,
            "name": name,
        }
    )


def decode_message(data):
    try:
        data = json.loads(data)
    except json.decoder.JSONDecodeError:
        logger.warning(f"Malformed JSON received: {data}")
        return None

    if (
        all(key in data for key in ("key", "sender", "origin", "name"))
        and data["key"] in KEYS
        and data["sender"] in SENDERS
        and data["origin"] in ORIGINS
        and isinstance(data["name"], str)
    ):
        # TODO proper name validation
        return [data["key"], data["sender"], data["origin"], data["name"]]
    else:
        logger.warning(f"Malformed data received: {data}")
        return None
