from typing import Union, Dict, Any, List
from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
from logger import logger
from batch_handler import BatchHandler

class InferenceData(BaseModel):
    model_id: str
    data: Dict[str, Any]


app = FastAPI()
result = [0]

async def callback_fn(batch: List[Dict]):
    logger.info("Received batch, doing work....")
    await asyncio.sleep(1)
    result[0] += 1
    results = [{"uid": item['uid'], "data": {"result": result[0]}} for item in batch]
    return results


from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    app.batch_handler = BatchHandler(max_batch_size=8, batch_timeout_ms=200, callback_fn=callback_fn)
    asyncio.create_task(app.batch_handler.consume())

@app.post("/inference")
async def inference(data: InferenceData):
    reply = await app.batch_handler.append(data.dict())
    logger.info("Done!")
    return reply
