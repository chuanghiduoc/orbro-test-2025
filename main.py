"""Main - UDP Server for receiving and processing Tag data."""

import socket
import threading
from datetime import datetime
from typing import Dict
from parser import TagParser, TagData
from db import db


class TagState:

    def __init__(self):
        self.data: Dict[str, dict] = {}
        self.lock = threading.Lock()

    def update(self, tag_data: TagData) -> bool:
        with self.lock:
            tag_id = tag_data.tag_id
            old_cnt = self.data.get(tag_id, {}).get("last_cnt")

            self.data[tag_id] = {
                "last_cnt": tag_data.cnt,
                "last_seen": tag_data.timestamp
            }

            return old_cnt != tag_data.cnt

    def get(self, tag_id: str) -> dict:
        with self.lock:
            return self.data.get(tag_id)

    def get_all(self) -> Dict[str, dict]:
        with self.lock:
            return dict(self.data)


tag_state = TagState()


class TagReceiver:

    def __init__(self, host: str = "0.0.0.0", port: int = 5000):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.running = False

    def start(self):
        self.sock.bind((self.host, self.port))
        self.running = True
        print(f"Tag Receiver started on {self.host}:{self.port}")
        print("-" * 60)

        try:
            while self.running:
                data, addr = self.sock.recvfrom(1024)
                self._process_data(data.decode())
        except KeyboardInterrupt:
            print("\nReceiver stopped")
        finally:
            self.sock.close()

    def _process_data(self, raw_data: str):
        tag_data = TagParser.parse(raw_data)
        if not tag_data:
            print(f"[ERROR] Invalid data: {raw_data}")
            return

        cnt_changed = tag_state.update(tag_data)

        if db.is_tag_registered(tag_data.tag_id):
            db.log_tag_data(tag_data.tag_id, tag_data.cnt, tag_data.timestamp)

        if cnt_changed:
            print(f"[CNT CHANGED] Tag: {tag_data.tag_id}, CNT: {tag_data.cnt}, "
                  f"Time: {tag_data.timestamp.isoformat()}")

    def stop(self):
        self.running = False


if __name__ == "__main__":
    receiver = TagReceiver()
    receiver.start()
