import asyncio
from time import perf_counter
from typing import List

from fastapi import FastAPI

from batch_handler import BatchHandler
from data_models import InferenceRequest
from logger import logger
from model import Model
from utils import b64image_to_pil

my_model = Model()

batch_id = [-1]
app = FastAPI()


def callback_fn(batch: List[dict]) -> List[dict]:
    batch_id[0] += 1
    logger.info(f"[🦾] received {len(batch)} elements, doing work....")
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


app = FastAPI()


@app.on_event("startup")
async def startup_event():
    app.batch_handler = BatchHandler(
        max_batch_size=16, batch_timeout_ms=10, callback_fn=callback_fn
    )

    asyncio.create_task(asyncio.to_thread(app.batch_handler.consume))


@app.post("/inference")
async def inference(req: InferenceRequest):
    start = perf_counter()
    res = await app.batch_handler.append(req.data.dict())
    logger.info(f"[✅] Done in {(perf_counter() - start) * 1000:.2f}ms")
    return res
