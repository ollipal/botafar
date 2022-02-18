import asyncio
import traceback

import websockets

from ..log_formatter import get_logger
from .json_utils import decode_message, encode_message

logger = get_logger()


class Server:
    def __init__(self, event_handler):
        self._event_handler = event_handler
        self._server = None
        self._loop = None

    async def _server_start(self, websocket, path):
        assert self._server is not None

        # self._event_handler("connect")
        while True:
            try:
                data = await websocket.recv()
            except websockets.exceptions.ConnectionClosedError as e:
                # self._event_handler("disconnect")
                logger.info("disconnected")  # TODO in event handler
                logger.debug(f"Server disconnected error: {e}")
                break
            except websockets.exceptions.ConnectionClosedOK as e:
                # self._event_handler("disconnect")
                logger.info("disconnected")  # TODO in event handler
                logger.debug(f"Server disconnected ok: {e}")
                break
            except Exception as e:
                traceback.print_exc()
                self.stop()
                break

            data = decode_message(data)
            if data is not None:
                # TODO in event handler
                if data[3] == "connect":
                    logger.info(f"{data[2]} connected as {data[1]}")

                self._event_handler(data)

    async def send(self, event, value=None, player=None):
        assert (
            self._server is not None
        ), "Server.serve() not called before .send()"

        try:
            await self._server.send(
                {
                    "event": event,
                    "value": value,
                    "player": player,
                }
            )
        except websockets.exceptions.ConnectionClosedError as e:
            logger.debug(f"Server.send failed: {e}")
        except websockets.exceptions.ConnectionClosedOK as e:
            logger.debug(f"Server.send failed: {e}")

    def stop(self):
        if self._stop is None:
            logger.debug(f"Server.stop skipped, serving not started?")
            return
        self._loop.call_soon_threadsafe(self._stop.set)

    async def serve(self, port):
        self._stop = asyncio.Event()
        self._loop = asyncio.get_running_loop()
        async with websockets.serve(self._server_start, port=port) as server:
            self._server = server
            await self._stop.wait()


if __name__ == "__main__":

    def event_handler(event):
        print(f"event={event}")

    async def main():
        server = Server(event_handler)
        await server.serve(8080)

    asyncio.run(main())
