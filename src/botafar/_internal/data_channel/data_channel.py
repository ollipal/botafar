import asyncio
import json
import logging
import os
import string
import warnings
from os import path
from random import Random
from sys import argv
from uuid import getnode

import socketio

# Ignore _SLOW_CRC32C_WARNING on Raspberry Pis
# content can be found here:
# https://github.com/googleapis/python-crc32c/blob/main/src/google_crc32c/__init__.py
with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=RuntimeWarning)
    from aiortc import (
        RTCConfiguration,
        RTCIceServer,
        RTCPeerConnection,
        RTCSessionDescription,
    )

from aiortc.sdp import candidate_from_sdp
from cryptography.utils import CryptographyDeprecationWarning

from ..events import SystemEvent
from ..log_formatter import get_logger
from ..string_utils import error_to_string
from .json_utils import parse_event

logger = get_logger()

# Removes a wrning from logs
# For some reason, updating relevant modules did to help...
warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)


def get_id():
    # Get id based on device mac address and file executed
    # As a result, restarting the program will re-connect to browser nicely
    # With no collisions between different devices
    full_path = path.abspath(argv[0])
    mac = str(getnode())
    rand = Random(full_path + mac)
    id = "".join(
        [
            rand.choice(string.ascii_lowercase + string.digits)
            for _ in range(18)
        ]
    )
    return f"{id[:6]}-{id[6:12]}-{id[12:]}"


def get_peer_connection_and_datachannel():
    pc = RTCPeerConnection(
        RTCConfiguration([RTCIceServer("stun:stun.l.google.com:19302")])
    )
    dc = pc.createDataChannel(
        "communication", negotiated=True, ordered=False, id=0
    )
    return pc, dc


def parse_message(message):
    message_type = message.get("type")
    request_id = message.get("requestId")
    data = message.get("data")

    return message_type, request_id, data


# From: https://stackoverflow.com/a/45430833
class Timer:
    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback
        self._task = asyncio.ensure_future(self._job())

    async def _job(self):
        await asyncio.sleep(self._timeout)
        await self._callback()

    def cancel(self):
        self._task.cancel()


class DataChannel:
    def __init__(self, process_event):
        self.process_event = process_event  # TODO use
        self.loop = None
        self.id = get_id()  # is read directly from outside
        self.peer_connection = None
        self.data_channel = None
        self.request_id = None
        self.sio = None
        self.create_sio_lock = asyncio.Lock()
        self.timer = None
        self._stop = None  # asyncio.Event()
        self._connected = False
        if os.environ.get("BOTAFAR_ENV") == "dev":
            logger.info("BOTAFAR_ENV=dev detected")
            self.url = "http://localhost:4005"
        else:
            self.url = "https://tb-signaling.onrender.com"
        self.has_connected = False  # is read directly from outside

    def _send_internal_datachannel_message(self, message_type):
        if self.data_channel is not None and self.request_id is not None:
            try:
                self.data_channel.send(
                    json.dumps(
                        {
                            "type": "INTERNAL_MESSAGE",
                            "data": {
                                "type": message_type,
                                "requestId": self.request_id,
                            },
                        }
                    )
                )
            except Exception as e:
                logger.debug("Could not send datachannel message", e)
        else:
            logger.debug(f"Not sending {message_type}")

    async def _create_sio(self):
        async with self.create_sio_lock:
            browser_disconnect_event = SystemEvent(
                "browser_disconnect", "library"
            )
            self.process_event(browser_disconnect_event)

            if self.sio is not None:
                await self.sio.disconnect()

            self._connected = False
            event = SystemEvent(
                "owner_disconnect", "server", text="create sio"
            )
            self.process_event(event)

            # Silence all logging
            socketio_logger = logging.getLogger("socketio")
            socketio_logger.addFilter(lambda record: False)
            engineio_logger = logging.getLogger("engineio")
            engineio_logger.addFilter(lambda record: False)

            # ssl_verify=False fixes MacOS SSL: CERTIFICATE_VERIFY_FAILED
            # More discussion here: https://stackoverflow.com/q/42098126
            # Running this could be another solution:
            # bash /Applications/Python*/Install\ Certificates.command
            self.sio = socketio.AsyncClient(
                logger=socketio_logger,
                engineio_logger=engineio_logger,
                reconnection=False,
                handle_sigint=False,
                ssl_verify=False,
            )

            @self.sio.on("message")
            async def message(recipient_id, message):
                await self._handle_internal_message(recipient_id, message)

            @self.sio.event
            def connect():
                logger.debug("sio connected")

            @self.sio.event
            def connect_error(data):
                logger.debug("sio error", data)

            @self.sio.event
            def disconnect():
                logger.debug("sio disconnected")

            try:
                await self.sio.connect(
                    self.url, wait=True, wait_timeout=5, transports="websocket"
                )
            except socketio.exceptions.ConnectionError:
                logger.error("Could not connect to server, try again later")
                await self.stop_async()
                return

            await self.sio.emit("setAliases", data=[self.id])

    async def _handle_internal_message(  # noqa: C901
        self, recipient_id, message
    ):
        message_type, request_id, data = parse_message(message)

        # Check types, data type can be anything
        if not (
            isinstance(message_type, str)
            and isinstance(request_id, str)
            and isinstance(recipient_id, str)
        ):
            logger.debug("Malformed internal message", recipient_id, message)
            return

        if self.request_id is not None and request_id != self.request_id:
            await self.sio.emit(
                "message",
                (
                    request_id,
                    {
                        "data": "Bot occupied",
                        "type": "requestDenied",
                        "requestId": request_id,
                    },
                ),
            )
            logger.debug("Browser denied")
            return

        if message_type == "ping":

            async def cb():
                logger.debug("Ping timeout")
                await self._create_sio()

            if self.timer is not None:
                self.timer.cancel()
            self.timer = Timer(3, cb)

            try:
                self.data_channel.send(
                    json.dumps(
                        {
                            "type": "INTERNAL_MESSAGE",
                            "data": {"type": "pong", "requestId": request_id},
                        }
                    )
                )
            except Exception as e:
                logger.debug("Could not send datachannel message", e)

        elif message_type == "requestOffer":
            # destroy old
            if self.data_channel is not None:
                self.data_channel.close()
            if self.peer_connection is not None:
                await self.peer_connection.close()

            self.data_channel = None
            self.peer_connection = None
            self.request_id = request_id

            (
                self.peer_connection,
                self.data_channel,
            ) = get_peer_connection_and_datachannel()

            @self.data_channel.on("close")
            async def on_dc_close():
                logger.debug("dc close")

            @self.data_channel.on("open")
            async def on_dc_open():
                logger.debug("dc open")
                self.has_connected = True
                self._connected = True

            @self.data_channel.on("message")
            async def on_message(message):
                try:
                    loaded_message = json.loads(message)
                    if loaded_message["type"] == "INTERNAL_MESSAGE":
                        await self._handle_internal_message(
                            recipient_id, loaded_message["data"]
                        )
                    else:
                        event = parse_event(message)
                        if event is not None:
                            self.process_event(event)
                        else:
                            logger.debug("Could not parse event")

                except Exception as e:
                    logger.debug("Could not handle datachannel message", e)

            @self.peer_connection.on("iceconnectionstatechange")
            async def iceconnectionstatechange():
                if self.peer_connection.iceConnectionState == "failed":
                    # same as otherNuked
                    """if dcs.get("owner"):
                        print("CLOSing dc")
                        dcs["owner"].close()
                    if pcs.get("owner"):
                        print("CLOSing peer")
                        await pcs["owner"].close()

                    # TODO close somehow?
                    pcs["owner"] = None
                    dcs["owner"] = None"""

                    try:
                        await self._create_sio()
                    except socketio.exceptions.ConnectionError:
                        pass  # Already connected

            @self.peer_connection.on("onicecandidate")
            def onicecandidate(candidate):
                logger.debug("ice candidate", candidate)

            try:
                await self.peer_connection.setLocalDescription(
                    await self.peer_connection.createOffer()
                )
                offer_data = {
                    "sdp": self.peer_connection.localDescription.sdp,
                    "type": self.peer_connection.localDescription.type,
                }
                await self.sio.emit(
                    "message",
                    (
                        request_id,
                        {
                            "data": offer_data,
                            "type": "offer",
                            "requestId": request_id,
                        },
                    ),
                )
            except Exception as e:
                logger.debug("Could not create or send offer", e)
        elif message_type == "answer":
            try:
                await self.peer_connection.setRemoteDescription(
                    RTCSessionDescription(data["sdp"], data["type"])
                )
            except Exception as e:
                logger.debug("Could not set remote description", e)
        elif message_type == "candidate":
            try:
                if data is None or data["candidate"] == "":
                    logger.debug(f"skipped candidate: {data}")
                    return

                candidate = candidate_from_sdp(
                    data["candidate"].split(":", 1)[1]
                )
                candidate.sdpMid = data["sdpMid"]
                candidate.sdpMLineIndex = data["sdpMLineIndex"]
                await self.peer_connection.addIceCandidate(candidate)
            except Exception as e:
                logger.debug("Could not add ice candidate", e)
        elif message_type == "otherNuked":
            # destroy old
            if self.data_channel is not None:
                self.data_channel.close()
            if self.peer_connection is not None:
                await self.peer_connection.close()

            self.data_channel = None
            self.peer_connection = None

            await self._create_sio()
        elif message_type == "connectionStable":
            if self.sio is not None:
                await self.sio.disconnect()
        else:
            logger.debug("Unknown internal message", message)

    async def serve(self):
        self.loop = asyncio.get_running_loop()
        self._stop = asyncio.Event()

        await self._create_sio()

        try:
            await self._stop.wait()
        finally:
            await self.stop_async()

    async def send(self, event):
        assert self.loop is not None, "serve() not called before .send()"

        if self.data_channel is None:
            logger.debug("No datachannel, not sending")
            return

        try:
            self.data_channel.send(event._to_json())
        except Exception as e:
            logger.debug(f"Unecpected send() error:\n{error_to_string(e)}")

    @property
    def connected(self):
        return self._connected

    async def stop_async(self):
        if self._stop is None:
            logger.debug("Server.stop_async skipped, serving not started?")
            return

        self._stop.set()
        if self.sio is not None:
            await self.sio.disconnect()
        self._connected = False

        if self.data_channel is not None:
            try:
                # self._send_internal_datachannel_message("otherNuked")
                self.data_channel.close()
            except Exception:
                pass
        if self.peer_connection is not None:
            try:
                await self.peer_connection.close()
            except Exception:
                pass
        # self._stop.set()

    def stop(self):
        if self._stop is None:
            logger.debug("Server.stop skipped, serving not started?")
            return

        self._stop.set()


if __name__ == "__main__":
    import signal

    dc = DataChannel(None)

    original_sigint_handler = signal.getsignal(signal.SIGINT)

    def signal_handler(_signal, frame):
        signal.signal(signal.SIGINT, original_sigint_handler)  # Reset
        dc.stop()

    signal.signal(signal.SIGINT, signal_handler)

    asyncio.run(dc.serve())
