import websockets

from ..log_formatter import get_logger
from .json_utils import decode_message, encode_message

from ..string_utils import error_to_string

logger = get_logger()


class Client:
    def __init__(self, port):
        self.port = port
        self.websocket = None

    async def receive(self):
        assert (
            self.websocket is not None
        ), "Client.connect() not called before .receive()"
        try:
            data = await self.websocket.recv()
        except websockets.exceptions.ConnectionClosed:
            return None  # TODO maybe indicate was closed?

        return decode_message(data)

    async def send(self, key, sender, origin, name):
        assert (
            self.websocket is not None
        ), "Client.connect() not called before .send()"
        try:
            await self.websocket.send(
                encode_message(key, sender, origin, name)
            )
            return True
        except websockets.exceptions.ConnectionClosedError as e:
            logger.debug(f"Client.send connection closed error: {e}")
        except websockets.exceptions.ConnectionClosedOK as e:
            logger.debug(f"Client.send connection closed: {e}")
        except Exception as e:
            logger.error(error_to_string(e))
        return False

    async def stop(self):
        if self.websocket is None:
            logger.debug("Client.stop skipped, not connected?")
            return
        await self.websocket.close()

    async def connect(self):
        self.websocket = await websockets.connect(
            f"ws://localhost:{self.port}"
        )
