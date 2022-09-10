import asyncio
from asyncio import constants
from asyncio.log import logger
from time import sleep

import websockets

""" from ..events import SystemEvent
from ..log_formatter import get_logger
from ..string_utils import error_to_string
from .json_utils import parse_event

logger = get_logger() """

import json
import string
import warnings
from secrets import choice
from uuid import uuid4

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

loop = asyncio.new_event_loop()
_stop = asyncio.Event()


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


""" class Datachannel:
    def __init__(self, process_event):
        self.creator_id = get_id()
        self.player_id = get_id()
        self.creator_peer_connection = None
        self.player_peer_connection = None

        self.process_event = process_event
        self.server = None
        self.loop = None
        self._stop = None

        self._connected = False

    async def send_owner(self, event):
        try:
            await asyncio.wait_for(
                connection.send(event._to_json()), timeout=0.5
            )
        except asyncio.TimeoutError:
            logger.warning("Send failed")
        except Exception as e:
            logger.error(
                f"Unecpected Server.send error:\n{error_to_string(e)}"
            )
            self.stop()

    async def send_creator(self, event):
        pass

    def kick_player():
        pass

    async def stop_async(self):
        if self._stop is None:
            logger.debug("Server.stop skipped, serving not started?")
            return

        try:
            await self._stop.set
        except RuntimeError:
            logger.debug("_stop.set failed")

    def stop(self):
        if self._stop is None:
            logger.debug("Server.stop skipped, serving not started?")
            return

        try:
            self.loop.call_soon_threadsafe(self._stop.set)
        except RuntimeError:
            logger.debug("call_soon_threadsafe errored")


    async def serve(self):
        self._stop = asyncio.Event()
        self.loop = asyncio.get_running_loop()

        sio = socketio.AsyncClient()

        # handlers

        await sio.connect('https://tb-signaling.onrender.com', transports="websocket")
        await sio.emit('setAliases', data=[self.creator_id, self.player_id])
        self._connected = True
        await self._stop.wait()
        await sio.disconnect()
        self._connected = False

    @property
    def connected(self):
        return self._connected """


async def main():
    pcs = {}
    dcs = {}
    reqs = {}
    sios = {}

    async def create_sio():
        if sios.get("owner"):
            await sios["owner"].disconnect()

        id = "bot"
        import logging

        socketio_logger = logging.getLogger("socketio")
        socketio_logger.addFilter(lambda record: False)

        engineio_logger = logging.getLogger("engineio")
        engineio_logger.addFilter(lambda record: False)

        """ logger=socketio_logger,
        engineio_logger=engineio_logger, """

        sio = socketio.AsyncClient(
            logger=socketio_logger,
            engineio_logger=engineio_logger,
            reconnection=False,
            handle_sigint=False,
        )

        sios["owner"] = sio

        @sio.on("message")
        async def message(recipient_id, message):
            await handle_internal_message(recipient_id, message)

        @sio.event
        def connect():
            print("I'm connected!")

        @sio.event
        def connect_error(data):
            print("The connection failed!")

        @sio.event
        def disconnect():
            print("I'm disconnected!")

        await sio.connect("http://localhost:4005", transports="websocket")
        #await sio.connect('https://tb-signaling.onrender.com', transports="websocket")
        await sio.emit("setAliases", data=[id])

    def send_internal_datachannel_message(message_type):
        datachannel = dcs["owner"]
        request_id = reqs["owner"]
        try:
            datachannel.send(
                json.dumps(
                    {
                        "type": "INTERNAL_MESSAGE",
                        "data": {
                            "type": message_type,
                            "requestId": request_id,
                        },
                    }
                )
            )
        except Exception as e:
            print(
                "Could not send datachannel message", e
            )  # ERROR TO STRING, LOGGER

    async def handle_internal_message(recipient_id, message):
        message_type, request_id, data = parse_message(message)

        # Check types, data type can be anything
        if not (
            isinstance(message_type, str)
            and isinstance(request_id, str)
            and isinstance(recipient_id, str)
        ):
            print("Malformed internal message", recipient_id, message)
            return

        reqs["owner"] = request_id

        if message_type == "ping":
            datachannel = dcs["owner"]
            try:
                datachannel.send(
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
            (
                peer_connection,
                datachannel,
            ) = get_peer_connection_and_datachannel()

            pcs["owner"] = peer_connection
            dcs["owner"] = datachannel

            @datachannel.on("open")
            async def on_dc_open():
                print("DATACHANNEL OPEN")
                await sios["owner"].disconnect()
                
                # datachannel.send(json.dumps({ "type": 'EXTERNAL_MESSAGE', "key": "test" }))

            @datachannel.on("message")
            async def on_message(message):
                # print("DATACHANNEL MESSAGE")
                try:
                    message = json.loads(message)
                    if message["type"] == "INTERNAL_MESSAGE":
                        # print(message)
                        await handle_internal_message(
                            recipient_id, message["data"]
                        )
                    else:
                        print("Not handled message", message)
                except Exception as e:
                    print(
                        "Could not handle datachannel message", e
                    )  # ERROR TO STRING, LOGGER

            @peer_connection.on("iceconnectionstatechange")
            async def iceconnectionstatechange():
                print("ice state", peer_connection.iceConnectionState)

                if peer_connection.iceConnectionState == "failed":
                    # same as otherNuked
                    if dcs.get("owner"):
                        print("CLOSing dc")
                        dcs["owner"].close()
                    if pcs.get("owner"):
                        print("CLOSing peer")
                        await pcs["owner"].close()

                    # TODO close somehow?
                    pcs["owner"] = None
                    dcs["owner"] = None

                    # TODO reconnect sio
                    await create_sio()

            @peer_connection.on("onicecandidate")
            def iceconnectionstatechange(candidate):
                print("ice candidate", candidate)

            try:
                await peer_connection.setLocalDescription(
                    await peer_connection.createOffer()
                )
                await sios["owner"].emit(
                    "message",
                    (
                        "browser",
                        {
                            "data": {
                                "sdp": peer_connection.localDescription.sdp,
                                "type": peer_connection.localDescription.type,
                            },
                            "type": "offer",
                            "requestId": message["requestId"],
                        },
                    ),
                )
            except Exception as e:
                print(
                    "Could not create or send offer", e
                )  # ERROR TO STRING, LOGGER
        elif message_type == "answer":
            pc = pcs["owner"]
            try:
                await pc.setRemoteDescription(
                    RTCSessionDescription(data["sdp"], data["type"])
                )
            except Exception as e:
                print(
                    "Could not set remote description", e
                )  # ERROR TO STRING, LOGGER
        elif message_type == "candidate":
            # print("CANDIDATE")
            # print(pcs["owner"])
            pc = pcs["owner"]
            try:
                if data is None or data["candidate"] == "":
                    print("skipped candidate:", data)
                    return

                candidate = candidate_from_sdp(
                    data["candidate"].split(":", 1)[1]
                )
                candidate.sdpMid = data["sdpMid"]
                candidate.sdpMLineIndex = data["sdpMLineIndex"]
                await pc.addIceCandidate(candidate)
            except Exception as e:
                print(
                    "Could not add ice candidate", e
                )  # ERROR TO STRING, LOGGER
                print(data)
        elif message_type == "otherNuked":
            if dcs.get("owner"):
                print("CLOSing dc")
                dcs["owner"].close()
            if pcs.get("owner"):
                print("CLOSing peer")
                await pcs["owner"].close()
            # TODO close somehow?
            pcs["owner"] = None
            dcs["owner"] = None

            await create_sio()
        else:
            print("Unknown internal message", message)

    # id = str(f"{uuid.uuid4()}_BOT")
    # asyncio
    
    
    await create_sio()

    try:
        print("PRE AWAITING")
        # await sio.wait()
        print("AWAITING")
        await _stop.wait()
    except:
        print("ERROR caught")
    finally:
        if dcs.get("owner"):
            print("CLOSing dc")
            send_internal_datachannel_message("otherNuked")

            # dcs["owner"].send(json.dumps({ "type": 'INTERNAL_MESSAGE', "data":  {
            #    "type": "otherNuked",
            #    } }))
            # await asyncio.sleep(1)
            try:
                dcs["owner"].close()
            except:
                print("Cole fail")
        if pcs.get("owner"):
            print("CLOSing peer")
            try:
                await pcs["owner"].close()
            except:
                print("Cole fail")
        _stop.set()
        print("CLOSED")
        await sios["owner"].disconnect()
    print("END")

    """ try:
        tasks = asyncio.all_tasks(asyncio.get_event_loop())
        for task in tasks:
            task.cancel()
    except RuntimeError as err:
        print('SIGINT or SIGTSTP raised')
        print("cleaning and exiting")
        sys.exit(1) """


if __name__ == "__main__":
    import signal
    import sys

    """ async def _signal_handler():
        print("SIGNAL")
        #await asyncio.sleep(1)
        try:
            tasks = asyncio.all_tasks(loop)
            for task in tasks:
                task.cancel()
        except RuntimeError as err:
            print("SIGINT or SIGTSTP raised")
            print("cleaning and exiting")
            sys.exit(1) """

    def signal_handler(*args):
        loop.call_soon_threadsafe(_stop.set)
        #loop.create_task(_signal_handler())

    signal.signal(signal.SIGINT, signal_handler)

    try:
        # asyncio.run(main())
        loop.run_until_complete(main())
    except RuntimeError:
        print("Errored")
        # raise
