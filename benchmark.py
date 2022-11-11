import base64
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from io import BytesIO
from pprint import pformat

import requests
from PIL import Image

from src.logger import logger

URL = "http://127.0.0.1:8000"

image = Image.open("./examples/cat.jpeg")
buffered = BytesIO()
image.save(buffered, format="JPEG")
img_str = base64.b64encode(buffered.getvalue())


@dataclass
class Report:
    tot_time: float
    tot_requests: int
    misses: int

    @property
    def time_per_request(self):
        return self.tot_time / self.tot_requests

    def print(self):
        print("🗒️ Report:")
        print(f"\tRun {self.tot_requests} in {self.tot_time:.4f}s.")
        print(f"\t{self.time_per_request:.4f}s/requests.")
        print(f"\t{self.misses / self.tot_requests * 100 :.2f}% misses.")


def make_request_json():
    return {"model_id": "test", "data": {"image": img_str.decode("utf-8")}}


class Benchmark:
    def __init__(
        self,
        num_requests: int = 100,
        num_threads: int = 8,
        sleep_between_requests: float = 0.05,
    ):
        self.num_requests = num_requests
        self.num_threads = num_threads
        self.sleep_between_requests = sleep_between_requests
        self.mean = []
        self.misses = 0

    def test(self, req_id):
        time.sleep(self.sleep_between_requests)
        start = time.time()
        logger.info(f"➡️ Sending request n = {req_id}")
        res = requests.post(f"{URL}/inference", json=make_request_json())
        try:
            elapsed = time.time() - start
            logger.info(f"⬅️ Received {pformat(res.json())} after {elapsed:.2f}s")
            self.mean.append(elapsed)
        except requests.exceptions.JSONDecodeError:
            self.misses += 1
            time.sleep(5)
            logger.error("💣 Invalid answer from the server")

    def __call__(self):
        with ThreadPoolExecutor(self.num_threads) as p:
            list(p.map(self.test, [i for i in range(self.num_requests)]))

    def make_report(self) -> Report:
        tot_time = sum(self.mean)

        return Report(
            tot_time=tot_time, tot_requests=len(self.mean), misses=self.misses
        )


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--num_requests", default=16, type=int)
    parser.add_argument("--num_threads", default=16, type=int)
    parser.add_argument("--sleep", default=1, type=float)

    args = parser.parse_args()
    num_requests, num_threads, sleep = args.num_requests, args.num_threads, args.sleep
    logger.info(f"Starting benchmark with {num_requests=}, {num_threads=}, {sleep=}")

    try:
        bm = Benchmark(num_requests, num_threads, sleep_between_requests=sleep)
        bm()
        bm.make_report().print()
    except KeyboardInterrupt:
        bm.make_report().print()
