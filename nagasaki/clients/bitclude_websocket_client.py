import _thread
import json
import time

import websocket

from nagasaki.event_manager import EventManager
from nagasaki.logger import logger
from nagasaki.models.bitclude import BitcludeEventOrderbook


class BitcludeWebsocketClient:
    def __init__(self, event_manager: EventManager):
        self.event_manager = event_manager
        self.ws = websocket.WebSocketApp(
            "wss://n1.ws.bitclude.com",
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )

    def on_message(self, ws, message):
        message_json = json.loads(message)

        if message_json["action"] == "orderbook":
            # logger.info(message_json)
            orderbook_event = BitcludeEventOrderbook(**message_json)
            self.event_manager.post_event("orderbook_changed", orderbook_event)

    def on_error(self, ws, error):
        logger.info(error)
        logger.exception(error)

    def on_close(self, ws, close_status_code, close_msg):
        logger.info("### closed ###")

    def on_open(self, ws: websocket.WebSocketApp):
        def run(*args):
            time.sleep(360)
            self.ws.close()
            logger.info("thread terminating...")

            _thread.start_new_thread(run, ())
