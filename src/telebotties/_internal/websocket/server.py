import asyncio

import websockets

from ..log_formatter import get_logger
from ..string_utils import error_to_string
from .json_utils import parse_event

logger = get_logger()


class Server:
    def __init__(self, event_handler):
        self.event_handler = event_handler
        self.server = None
        self.loop = None

    async def _server_start(self, websocket, path):
        assert self.server is not None

        # self.event_handler("connect")
        while True:
            try:
                data = await websocket.recv()
            except websockets.exceptions.ConnectionClosedError as e:
                # self.event_handler("disconnect")
                logger.info("disconnected")  # TODO in event handler
                logger.debug(f"Server disconnected error: {e}")
                break
            except websockets.exceptions.ConnectionClosedOK as e:
                # self.event_handler("disconnect")
                logger.info("disconnected")  # TODO in event handler
                logger.debug(f"Server disconnected ok: {e}")
                break
            except Exception as e:
                # TODO print error properly
                logger.error(f"Unecpected Server error:\n{error_to_string(e)}")
                self.stop()
                break

            event = parse_event(data)
            if event is not None:
                self.event_handler(event)

    async def send(self, event):
        assert (
            self.server is not None
        ), "Server.serve() not called before .send()"

        try:
            await self.server.send(event._to_json())
        except websockets.exceptions.ConnectionClosedError as e:
            logger.debug(f"Server.send failed, error: {e}")
        except websockets.exceptions.ConnectionClosedOK as e:
            logger.debug(f"Server.send failed, closed: {e}")
        except Exception as e:
            logger.error(
                f"Unecpected Server.send error:\n{error_to_string(e)}"
            )
            self.stop()

    def stop(self):
        if self._stop is None:
            logger.debug("Server.stop skipped, serving not started?")
            return
        self.loop.call_soon_threadsafe(self._stop.set)

    async def serve(self, port):
        self._stop = asyncio.Event()
        self.loop = asyncio.get_running_loop()
        async with websockets.serve(self._server_start, port=port) as server:
            self.server = server
            await self._stop.wait()


if __name__ == "__main__":

    def event_handler(event):
        print(f"event={event}")

    async def main():
        server = Server(event_handler)
        await server.serve(8080)

    asyncio.run(main())
