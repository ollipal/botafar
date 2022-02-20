import websockets

from ..log_formatter import get_logger
from ..string_utils import error_to_string
from .json_utils import parse_event

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

        return parse_event(data)

    async def send(self, event):
        assert (
            self.websocket is not None
        ), "Client.connect() not called before .send()"
        try:
            await self.websocket.send(event._to_json())
            return True
        except websockets.exceptions.ConnectionClosedError as e:
            logger.debug(f"Client.send connection closed error: {e}")
        except websockets.exceptions.ConnectionClosedOK as e:
            logger.debug(f"Client.send connection closed: {e}")
        except Exception as e:
            logger.debug(
                f"Unexpected Client.send error:\n{error_to_string(e)}"
            )
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
