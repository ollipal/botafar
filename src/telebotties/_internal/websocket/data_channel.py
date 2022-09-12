import asyncio
import logging
from ast import excepthandler
from asyncio import constants
from asyncio.log import logger
from time import sleep

import websockets

from ..events import SystemEvent
from ..log_formatter import get_logger
from ..string_utils import error_to_string
from .json_utils import parse_event

logger = get_logger()

import json
import string
import warnings
from secrets import choice
from uuid import uuid4

import aiortc.sdp as sdp
import socketio
from aiortc import (
    RTCConfiguration,
    RTCIceServer,
    RTCPeerConnection,
    RTCSessionDescription,
)
from aiortc.sdp import candidate_from_sdp, candidate_to_sdp
from cryptography.utils import CryptographyDeprecationWarning

# Removes a wrning from logs
# For some reason, updating relevant modules did to help...
warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)


# _stop = asyncio.Event()


def get_id():
    return "".join(
        [choice(string.ascii_lowercase + string.digits) for _ in range(16)]
    )


def get_peer_connection_and_datachannel():
    print("pc, dc created")
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
        self.id = "bot"  # get_id()
        self.peer_connection = None
        self.data_channel = None
        self.request_id = None
        self.sio = None
        self.create_sio_lock = asyncio.Lock()
        self.timer = None
        self._stop = asyncio.Event()
        self._connected = False
        self.url = "http://localhost:4005"
        #self.url = "https://tb-signaling.onrender.com"
        self.has_connected = False

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
                print(
                    "Could not send datachannel message", e
                )  # ERROR TO STRING, LOGGER
        else:
            print(f"Not sending {message_type}")

    async def _create_sio(self):
        async with self.create_sio_lock:
            if self.sio is not None:
                print("Sio disconnected")
                await self.sio.disconnect()

            self._connected = False

            # Silence all logging
            socketio_logger = logging.getLogger("socketio")
            socketio_logger.addFilter(lambda record: False)
            engineio_logger = logging.getLogger("engineio")
            engineio_logger.addFilter(lambda record: False)

            self.sio = socketio.AsyncClient(
                logger=socketio_logger,
                engineio_logger=engineio_logger,
                reconnection=False,
                handle_sigint=False,
            )

            @self.sio.on("message")
            async def message(recipient_id, message):
                await self._handle_internal_message(recipient_id, message)

            @self.sio.event
            def connect():
                print("I'm connected!")

            @self.sio.event
            def connect_error(data):
                print("The connection failed!")

            @self.sio.event
            def disconnect():
                print("I'm disconnected!")

            try:
                await self.sio.connect(self.url, wait=True, wait_timeout=5, transports="websocket")
            except socketio.exceptions.ConnectionError as e:
                logger.error(f"Could not connect to server")
                await self.stop_async()
                return
            
            await self.sio.emit("setAliases", data=[self.id])
            print("New connected")

    async def _handle_internal_message(self, recipient_id, message):
        message_type, request_id, data = parse_message(message)

        # Check types, data type can be anything
        if not (
            isinstance(message_type, str)
            and isinstance(request_id, str)
            and isinstance(recipient_id, str)
        ):
            print("Malformed internal message", recipient_id, message)
            return

        # print(request_id)
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
            print("DENIED")
            return

        if message_type == "ping":

            async def cb():
                print("CALLBACK")
                await self._create_sio()

            print("PING")
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
                print(
                    "Could not send datachannel message", e
                )  # ERROR TO STRING, LOGGER

        elif message_type == "requestOffer":
            # destroy old
            if self.data_channel is not None:
                print("CLOSing dc")
                self.data_channel.close()
            if self.peer_connection is not None:
                print("CLOSing peer")
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
                print("DATACHANNEL CLOSE")

            @self.data_channel.on("open")
            async def on_dc_open():
                print("DATACHANNEL OPEN")
                self.has_connected = True
                self._connected = True

                # datachannel.send(json.dumps({ "type": 'EXTERNAL_MESSAGE', "key": "test" }))

            @self.data_channel.on("message")
            async def on_message(message):
                # print("DATACHANNEL MESSAGE")
                try:
                    loaded_message = json.loads(message)
                    if loaded_message["type"] == "INTERNAL_MESSAGE":
                        # print(message)
                        await self._handle_internal_message(
                            recipient_id, loaded_message["data"]
                        )
                    else:
                        print("Parsing event", message)
                        event = parse_event(message)
                        if event is not None:
                            self.process_event(event)
                        else:
                            print("Event was None")
                        
                except Exception as e:
                    print(
                        "Could not handle datachannel message", e
                    )  # ERROR TO STRING, LOGGER

            @self.peer_connection.on("iceconnectionstatechange")
            async def iceconnectionstatechange():
                print("ice state", self.peer_connection.iceConnectionState)

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

                    # TODO reconnect sio
                    print("Creat1")
                    try:
                        # await sios["owner"].connect(url, transports="websocket")
                        await self._create_sio()
                    except socketio.exceptions.ConnectionError:
                        pass  # Already connected

            @self.peer_connection.on("onicecandidate")
            def iceconnectionstatechange(candidate):
                print("ice candidate", candidate)

            try:
                await self.peer_connection.setLocalDescription(
                    await self.peer_connection.createOffer()
                )
                await self.sio.emit(
                    "message",
                    (
                        request_id,
                        {
                            "data": {
                                "sdp": self.peer_connection.localDescription.sdp,
                                "type": self.peer_connection.localDescription.type,
                            },
                            "type": "offer",
                            "requestId": request_id,
                        },
                    ),
                )
            except Exception as e:
                print(
                    "Could not create or send offer", e
                )  # ERROR TO STRING, LOGGER
        elif message_type == "answer":
            try:
                await self.peer_connection.setRemoteDescription(
                    RTCSessionDescription(data["sdp"], data["type"])
                )
            except Exception as e:
                print(
                    "Could not set remote description", e
                )  # ERROR TO STRING, LOGGER
        elif message_type == "candidate":
            # print("CANDIDATE")
            # print(pcs["owner"])
            try:
                if data is None or data["candidate"] == "":
                    print("skipped candidate:", data)
                    return

                candidate = candidate_from_sdp(
                    data["candidate"].split(":", 1)[1]
                )
                candidate.sdpMid = data["sdpMid"]
                candidate.sdpMLineIndex = data["sdpMLineIndex"]
                await self.peer_connection.addIceCandidate(candidate)
            except Exception as e:
                print(
                    "Could not add ice candidate", e
                )  # ERROR TO STRING, LOGGER
                print(data)
        elif message_type == "otherNuked":
            # destroy old
            if self.data_channel is not None:
                print("CLOSing dc")
                self.data_channel.close()
            if self.peer_connection is not None:
                print("CLOSing peer")
                await self.peer_connection.close()

            self.data_channel = None
            self.peer_connection = None

            # await sios["owner"].connect(url, transports="websocket")
            await self._create_sio()
        elif message_type == "connectionStable":
            print("Disconnect2")
            if self.sio is not None:
                await self.sio.disconnect()
        else:
            print("Unknown internal message", message)

    async def serve(self):
        print("Creating main")
        self.loop = asyncio.get_running_loop()
        await self._create_sio()

        try:
            print("AWAITNG")
            await self._stop.wait()
        except KeyboardInterrupt:
            print("KEYBOARD")
        finally:
            await self.stop_async()
        print("END")

    async def send(self, event):
        print("------------------------- SENDING")
        assert (
            self.loop is not None
        ), "serve() not called before .send()"

        if self.data_channel is None:
            print("No datachannel")
            return

        try:
            self.data_channel.send(event._to_json())
        except Exception as e:
            logger.error(
                f"Unecpected send() error:\n{error_to_string(e)}"
            )

    @property
    def connected(self):
        return self._connected

    async def stop_async(self):
        self._stop.set()
        if self.sio is not None:
            await self.sio.disconnect()
        self._connected = False

        if self.data_channel is not None:
            print("CLOSing dc")
            try:
                # self._send_internal_datachannel_message("otherNuked")
                self.data_channel.close()
            except:
                print("Cole fail")
        if self.peer_connection is not None:
            print("CLOSing peer")
            try:
                await self.peer_connection.close()
            except:
                print("Cole fail")
        self._stop.set()

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
