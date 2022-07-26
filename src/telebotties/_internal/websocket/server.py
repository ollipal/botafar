import asyncio

import websockets

from ..events import SystemEvent
from ..log_formatter import get_logger
from ..string_utils import error_to_string
from .json_utils import parse_event

logger = get_logger()


class Server:
    def __init__(self, process_event):
        self.process_event = process_event
        self.server = None
        self.loop = None
        self._stop = None
        self._connections = set()
        self._connected = False

    async def _server_start(self, websocket, path):
        assert self.server is not None

        self._connections.add(websocket)
        try:
            while True:
                try:
                    data = await websocket.recv()
                except websockets.exceptions.ConnectionClosedError as e:
                    if len(self._connections) == 1:
                        event = SystemEvent(
                            "host_disconnect", "server", text=str(e)
                        )
                        self.process_event(event)
                    logger.debug(f"Server disconnected error: {e}")
                    break
                except websockets.exceptions.ConnectionClosedOK as e:
                    if len(self._connections) == 1:
                        event = SystemEvent(
                            "host_disconnect", "server", text=str(e)
                        )
                        self.process_event(event)
                    logger.debug(f"Server disconnected ok: {e}")
                    break
                except Exception as e:
                    if len(self._connections) == 1:
                        event = SystemEvent(
                            "host_disconnect", "server", text=str(e)
                        )
                        self.process_event(event)
                    logger.error(
                        f"Unecpected Server error:\n{error_to_string(e)}"
                    )
                    self.stop()
                    break

                event = parse_event(data)
                if event is not None:
                    self.process_event(event)
        finally:
            self._connections.remove(websocket)

    async def send(self, event):
        assert (
            self.server is not None
        ), "Server.serve() not called before .send()"

        slow_connections = []

        for connection in self._connections:
            try:
                await asyncio.wait_for(
                    connection.send(event._to_json()), timeout=0.5
                )
            except websockets.exceptions.ConnectionClosedError as e:
                logger.debug(f"Server.send failed, error: {e}")
            except websockets.exceptions.ConnectionClosedOK as e:
                logger.debug(f"Server.send failed, closed: {e}")
            except asyncio.TimeoutError:
                logger.warning("Connection.send was slow, closing soon...")
                slow_connections.append(connection)
            except Exception as e:
                logger.error(
                    f"Unecpected Server.send error:\n{error_to_string(e)}"
                )
                self.stop()
                break

            for slow_connection in slow_connections:
                try:
                    await asyncio.wait_for(connection.close(), timeout=0.5)
                except asyncio.TimeoutError:
                    logger.warning("Connection closing was slow, skipping...")

                self._connections.remove(slow_connection)

    async def stop_async(self):
        # Async handles connection closing as well
        await asyncio.gather(
            *[connection.close() for connection in self._connections]
        )
        self._connections = []
        self.stop()

    def stop(self):
        if self._stop is None:
            logger.debug("Server.stop skipped, serving not started?")
            return

        try:
            self.loop.call_soon_threadsafe(self._stop.set)
        except RuntimeError:
            logger.debug("call_soon_threadsafe errored")

        self._connected = False

    async def serve(self, port):
        self._stop = asyncio.Event()
        self.loop = asyncio.get_running_loop()
        # close_timeout=0.1 and ping interval/timeout make
        # connecting on Firefox way faster
        async with websockets.serve(
            self._server_start,
            port=port,
            ping_interval=1,
            ping_timeout=1,
            close_timeout=0.1,
        ) as server:
            self.server = server
            self._connected = True
            await self._stop.wait()

    @property
    def connected(self):
        return self._connected
