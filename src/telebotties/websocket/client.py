import asyncio
import traceback

import websockets

from ..log_formatter import get_logger
from .json_utils import decode_message, encode_message

logger = get_logger()


class Client:
    def __init__(self, port):
        self._port = port
        self._websocket = None

    async def receive(self):
        assert (
            self._websocket is not None
        ), "Client.connect() not called before .receive()"
        try:
            data = await self._websocket.recv()
        except websockets.exceptions.ConnectionClosed:
            return None  # TODO maybe indicate was closed?

        return decode_message(data)

    async def send(self, key, sender, origin, name):
        assert (
            self._websocket is not None
        ), "Client.connect() not called before .send()"
        try:
            await self._websocket.send(
                encode_message(key, sender, origin, name)
            )
            return True
        except websockets.exceptions.ConnectionClosedError as e:
            logger.debug(f"Client.send connection closed error: {e}")
        except websockets.exceptions.ConnectionClosedOK as e:
            logger.debug(f"Client.send connection closed: {e}")
        except Exception as e:
            exception_string = "".join(
                traceback.format_exception(type(e), e, e.__traceback__)
            )
            logger.error(exception_string)
        return False

    async def stop(self):
        if self._websocket is None:
            logger.debug(f"Client.stop skipped, not connected?")
            return
        await self._websocket.close()

    async def connect(self):
        self._websocket = await websockets.connect(
            f"ws://localhost:{self._port}"
        )
