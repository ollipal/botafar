import asyncio

import websockets

from ..events import SystemEvent
from ..log_formatter import get_logger
from ..string_utils import error_to_string
from .json_utils import parse_event

logger = get_logger()


class Client:
    def __init__(self, address, process_event):
        self.address = address
        self.process_event = process_event
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

            event = parse_event(data)
            if event is not None:
                self.process_event(event)

    async def send(self, event):
        assert (
            self.websocket is not None
        ), "Client.connect() not called before .send()"
        try:
            await self.websocket.send(event._to_json())
            return True
        except websockets.exceptions.ConnectionClosedError as e:
            logger.debug(f"Client.send connection closed error: {e}")
            event = SystemEvent("host_disconnect", None, text=str(e))
            self.process_event(event)
        except websockets.exceptions.ConnectionClosedOK as e:
            logger.debug(f"Client.send connection closed: {e}")
            event = SystemEvent("host_disconnect", None, text=str(e))
            self.process_event(event)
        except Exception as e:
            logger.debug(
                f"Unexpected Client.send error:\n{error_to_string(e)}"
            )
            event = SystemEvent("host_disconnect", None, text=str(e))
            self.process_event(event)
        return False

    async def stop(self):
        if self.websocket is None:
            logger.debug("Client.stop skipped, not connected?")
            return
        await self.websocket.close()

    async def connect(self):
        self.websocket = await websockets.connect(f"ws://{self.address}")

        # Check first send, it does not raise errors
        # (they do not seem to work as expected)
        connect_event = SystemEvent("host_connect", "host")
        success = await self.send(connect_event)
        if not success:
            await self.stop()
            raise ConnectionRefusedError

        try:
            reply = await asyncio.wait_for(self.websocket.recv(), timeout=1)
            event = parse_event(reply)
            if (
                event is not None
                and event.name == "connect_ok"
                and hasattr(event, "data")
            ):
                return event.data

            # Else, event.name is most likely "already_connected",
            # but it could be other events as well if just happened to send a
            # message to other connected client
            await self.stop()
            raise RuntimeError
        except (asyncio.TimeoutError, websockets.exceptions.ConnectionClosed):
            await self.stop()
            raise ConnectionRefusedError
