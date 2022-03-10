import websockets

from ..events import SystemEvent
from ..log_formatter import get_logger
from ..string_utils import error_to_string
from .json_utils import parse_event

logger = get_logger()


class Client:
    def __init__(self, port, receive_callback):
        self.port = port
        self.receive_callback = receive_callback
        self.websocket = None

    async def receive(self):
        assert (
            self.websocket is not None
        ), "Client.connect() not called before .receive()"

        while True:
            try:
                data = await self.websocket.recv()
            except websockets.exceptions.ConnectionClosed:
                break
                logger.info("CONNECTION CLOSED")

            self.receive_callback(parse_event(data))

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

    async def connect(self, connect_as):
        self.websocket = await websockets.connect(
            f"ws://localhost:{self.port}"
        )

        # Check first send, it does not raise errors
        # (they do not seem to work as expected)
        connect_event = SystemEvent("connect", connect_as, "", None)
        success = await self.send(connect_event)
        if not success:
            await self.stop()
            raise ConnectionRefusedError
