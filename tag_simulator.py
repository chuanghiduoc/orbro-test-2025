"""Tag Simulator - Generates simulated RTLS tag data via UDP socket."""

import socket
import time
import random
from datetime import datetime


class TagSimulator:

    def __init__(self, host: str = "127.0.0.1", port: int = 5000):
        self.host = host
        self.port = port
        self.tags = {
            "fa451f0755d8": 0,
            "ab123c456def": 0,
            "cd789e012fab": 0,
        }
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def generate_timestamp(self) -> str:
        now = datetime.now()
        return now.strftime("%Y%m%d%H%M%S") + f".{now.microsecond // 1000:03d}"

    def generate_tag_data(self, tag_id: str) -> str:
        self.tags[tag_id] += 1
        timestamp = self.generate_timestamp()
        return f"TAG,{tag_id},{self.tags[tag_id]},{timestamp}"

    def send_data(self, data: str):
        self.sock.sendto(data.encode(), (self.host, self.port))
        print(f"[SENT] {data}")

    def run(self, interval: float = 1.0):
        print(f"Tag Simulator started - sending to {self.host}:{self.port}")
        print(f"Simulating {len(self.tags)} tags: {list(self.tags.keys())}")
        print("-" * 60)

        try:
            while True:
                for tag_id in self.tags:
                    if random.random() > 0.3:
                        data = self.generate_tag_data(tag_id)
                        self.send_data(data)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nSimulator stopped")
        finally:
            self.sock.close()


if __name__ == "__main__":
    simulator = TagSimulator()
    simulator.run(interval=1.0)
