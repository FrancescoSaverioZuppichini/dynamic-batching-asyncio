import asyncio
import time
from logger import logger
from uuid import uuid4
import aiohttp
from typing import List, Awaitable


class LoadBalancer:
    def __init__(
        self,
        max_batch_size: int,
        batch_timeout_ms: int,
        worker_url: str,
        inference_request_timeout: int = 5,
    ) -> None:
        self._queue = []
        self._responses = {}
        self.max_batch_size = max_batch_size
        self.batch_timeout_ms = batch_timeout_ms
        self._last_batch_sent = time.time()
        self._client_session = aiohttp.ClientSession()
        self.worker_url = worker_url
        self.inference_request_timeout = inference_request_timeout

    async def send(self, data: dict) -> Awaitable:
        data["uid"] = str(uuid4())
        self._queue.append(data)
        return await self.wait_for_reply(data["uid"])

    async def send_batch_to_worker(self, batch: List[dict]):
        # send batch to workers
        async with self._client_session.post(
            self.worker_url, json=batch, timeout=self.inference_request_timeout
        ) as result:
            result.raise_for_status()
            data = await result.json()
            for item in data:
                self._responses[item["uid"]] = item

    async def consumer(self):
        # batch stuff in self._queue and send it to worker
        while True:
            await asyncio.sleep(0.1)
            while self._queue and (
                (len(self._queue) >= self.max_batch_size)
                or (
                    (time.time() - self._last_batch_sent) > self.batch_timeout_ms / 1000
                )
            ):
                batch = self._queue[: self.max_batch_size]
                self._queue = self._queue[self.max_batch_size :]
                self._last_batch_sent = time.time()
                logger.info(f"[📦] batched {len(batch)} requests")
                asyncio.create_task(self.send_batch_to_worker(batch))

    async def wait_for_reply(self, uid: str):
        # wait for a specific request identified by a uid
        while True:
            await asyncio.sleep(0.1)
            if uid in self._responses:
                response = self._responses[uid]
                del self._responses[uid]
                return response

    def shutdown(self):
        self._client_session.close()