import socket

from .log_formatter import get_logger

logger = get_logger()


# Adapted from: https://stackoverflow.com/a/28950776/7388328
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # Doesn't have to be reachable
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
        logger.debug("Could not get ip, defaulting to 127.0.0.1")
    finally:
        s.close()
    return ip
