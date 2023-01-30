import asyncio
from time import perf_counter
from typing import List

import grpc
from fastapi import FastAPI

import worker_pb2
import worker_pb2_grpc
from batch_handler import BatchHandler
from logger import logger
from model import Model
from utils import b64image_to_pil

my_model = Model()

batch_id = [-1]


def callback_fn(batch: List[dict]) -> List[dict]:
    batch_id[0] += 1
    start = perf_counter()
    images = [b64image_to_pil(item["image"]) for item in batch]
    preds = my_model.inference(images)
    # order is preserved
    results = [
        {"uid": item["uid"], "data": {"batch_id": batch_id[0], "pred": pred}}
        for item, pred in zip(batch, preds)
    ]
    logger.info(f"[🦾] Model tooks {(perf_counter() - start) * 1000:.2f}ms")
    return results


class Worker(worker_pb2_grpc.WorkerServicer):
    def __init__(self) -> None:
        self.batch_handler = BatchHandler(
            max_batch_size=16, batch_timeout_ms=10, callback_fn=callback_fn
        )
        asyncio.create_task(asyncio.to_thread(self.batch_handler.consume))

    async def inference(self, request: worker_pb2.InferenceRequest, context):
        logger.info(f"[🦾] Received request")
        start = perf_counter()
        res = await self.batch_handler.append({"image": request.data.image})
        data = res["data"]
        logger.info(f"[✅] Done in {(perf_counter() - start) * 1000:.2f}ms")
        return worker_pb2.InferenceReply(batch_id=data["batch_id"], pred=data["pred"])


async def serve():
    server = grpc.aio.server()
    worker_pb2_grpc.add_WorkerServicer_to_server(Worker(), server)
    listen_addr = "[::]:50053"
    server.add_insecure_port(listen_addr)
    logger.info(f"Starting server on {listen_addr}")
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
