import base64
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from io import BytesIO
from pprint import pformat
from typing import List
import pandas as pd
import requests
from PIL import Image
from pathlib import Path
from src.logger import logger
import numpy as np
URL = "http://127.0.0.1:8000"

image = Image.open("./examples/cat.jpeg")
buffered = BytesIO()
image.save(buffered, format="JPEG")
img_str = base64.b64encode(buffered.getvalue())


@dataclass
class Report:
    times: List[float]
    misses: int
    
    
    def compute_stats(self) -> dict:
        times_ms = np.array(self.times) * 1000
        return dict(
            mean = [times_ms.mean()],
            min = [times_ms.min()],
            max = [times_ms.max()]
        )

    def to_df(self, **kwargs) -> pd.DataFrame:
        df = pd.DataFrame(
            data={
                **self.compute_stats(),
                **kwargs,
            }
        )

        return df

    def to_csv(self, filepath: Path, **kwargs):
        df = self.to_df(**kwargs)
        if filepath.exists():
            old_df = pd.read_csv(filepath)
            df = pd.concat([old_df, df])
        df.to_csv(filepath, index=False)


    def print(self):
        print("🗒️ Report:")
        print(self.to_df())


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
        self.times = []
        self.misses = 0

    def test(self, req_id):
        time.sleep(self.sleep_between_requests)
        start = time.perf_counter()
        logger.info(f"➡️ Sending request n = {req_id}")
        res = requests.post(f"{URL}/inference", json=make_request_json())
        try:
            elapsed = time.perf_counter() - start
            logger.info(f"⬅️ Received {pformat(res.json())} after {elapsed * 1000:.2f}ms")
            self.times.append(elapsed)
        except requests.exceptions.JSONDecodeError:
            self.misses += 1
            time.sleep(5)
            logger.error("💣 Invalid answer from the server")

    def __call__(self):        
        with ThreadPoolExecutor(self.num_threads) as p:
            # warmap
            list(p.map(self.test, [i for i in range(8)]))
            self.times = []
            self.misses  = 0
            list(p.map(self.test, [i for i in range(self.num_requests)]))

    def make_report(self) -> Report:
        return Report(
            times=self.times, misses=self.misses
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
        bm.make_report().to_csv(Path("./benchmark.csv"), **dict(
            num_threads=num_threads,
            num_requests=num_requests,
            sleep=sleep
        ))
    except KeyboardInterrupt:
        bm.make_report().print()
