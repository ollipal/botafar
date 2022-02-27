from ..callback_executor import CallbackExecutor
from ..constants import SYSTEM_EVENT
from ..log_formatter import get_logger, setup_logging
from ..states import KeyboardClientState
from ..string_utils import error_to_string
from ..websocket import Client
from .telebotties_base import TelebottiesBase

logger = get_logger()


class Cli(TelebottiesBase):
    def __init__(self):
        self.callback_executor = CallbackExecutor(
            self.done_callback, self.error_callback
        )
        self.state = KeyboardClientState(self.send_event)
        super().__init__()
        self.client = None
        self.callback_executor.add_to_takes_event(self._send_event_async)

    def send_event(self, event):
        self.callback_executor.execute_callbacks(
            [self._send_event_async], event=event
        )

    async def _send_event_async(self, event):
        send_success = await self.client.send(event)
        if not send_success or (
            event._type == SYSTEM_EVENT and event.name == "client_disconnect"
        ):
            if (
                event._type == SYSTEM_EVENT
                and event.name == "client_disconnect"
            ):
                logger.debug("client_disconnect detected")
            return False

    async def main(self):
        try:
            self.client = Client(8080)
            try:
                await self.client.connect(connect_as="player")
            except ConnectionRefusedError:
                print(
                    "Connection refused to 127.0.0.1:8080, "
                    "wrong address or bot not running?"
                )
                return

            await self.keyboard_listener.run_until_finished()
            await self.client.stop()
        except Exception as e:
            logger.error(f"Unexpected internal error: {error_to_string(e)}")
            self.keyboard_listener.stop()
            if self.client is not None:
                await self.client.stop()

    def done_callback(self, future):
        if future.result() is False:  # Send failed or Esc pressed
            logger.info("Keyboard disconnected")
            self.keyboard_listener.stop()

    def sigint_callback(self):
        pass


def _cli():
    setup_logging("DEBUG")
    Cli().run()
