import asyncio
import time
from typing import Awaitable, List
from uuid import uuid4

from logger import logger


class BatchHandler:
    def __init__(
        self,
        max_batch_size: int,
        batch_timeout_ms: int,
        callback_fn: Awaitable,
        inference_request_timeout: int = 5,
    ) -> None:
        self._queue = []
        self._responses = {}
        self.max_batch_size = max_batch_size
        self.batch_timeout_ms = batch_timeout_ms
        self._last_batch_sent = time.time()
        self.callback_fn = callback_fn
        self.inference_request_timeout = inference_request_timeout

    async def append(self, data: dict) -> Awaitable:
        # add an unique idenfitier
        data["uid"] = str(uuid4())
        self._queue.append(data)
        return await self.wait_for_reply(data["uid"])

    async def collect_replies(self, batch: List[dict]):
        data = await self.callback_fn(batch)
        for item in data:
            self._responses[item["uid"]] = item

    async def consume(self):
        # batch stuff and send to self.callback_fn
        while True:
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
                asyncio.create_task(self.collect_replies(batch))

            await asyncio.sleep(0.1)

    async def wait_for_reply(self, uid: str) -> dict:
        # wait for a specific request identified by a uid
        while True:
            if uid in self._responses:
                response = self._responses[uid]
                del self._responses[uid]
                return response
            await asyncio.sleep(0.1)


if __name__ == "__main__":
    from pprint import pprint

    async def main():
        async def callback_fn(batch: List[dict]) -> List[dict]:
            print(f"Processing items with uid = {[item['uid'] for item in batch]}")
            return batch

        handler = BatchHandler(
            max_batch_size=32, batch_timeout_ms=200, callback_fn=callback_fn
        )
        # start the consumer, will look at stuff on the queue to batch
        asyncio.create_task(handler.consume())
        # sendint one item
        res = await handler.append({"foo": "baa"})
        pprint(res)
        # sending more at the same time
        res = await asyncio.gather(
            handler.append({"foo": "baa"}),
            handler.append({"foo": "baa1"}),
            handler.append({"foo": "baa2"}),
        )
        pprint(res)

    asyncio.run(main())
