import _thread
import json
import logging
import time
from datetime import datetime

import websocket
from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from websocket_logger.settings import Settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
logger.addHandler(logging.StreamHandler())
Base = declarative_base()


class WebsocketEvent(Base):
    __tablename__ = "websocket_event"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String)
    time = Column(DateTime, default=datetime.now)


class BitcludeWebsocketClient:
    def __init__(self, session):
        self.session = session
        self.ws = websocket.WebSocketApp(
            "wss://n1.ws.bitclude.com",
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )

    def on_message(self, ws, message):
        message_json = json.loads(message)
        logger.info(message_json)

        if message_json["action"] == "orderbook" and message_json["symbol"] in (
            "ETH_PLN",
            "BTC_PLN",
        ):
            with self.session() as db:
                db.add(WebsocketEvent(message=message))
                db.commit()
                db.close()

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


def main():
    # engine = create_engine(
    #     url="sqlite:///:memory:",
    #     connect_args={"check_same_thread": False},
    #     poolclass=StaticPool,
    #     echo=True,
    # )
    logger.info("starting...")
    settings = Settings()
    engine = create_engine(url=settings.connection_string)

    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)
    bc = BitcludeWebsocketClient(session)
    bc.ws.run_forever()


if __name__ == "__main__":
    main()
