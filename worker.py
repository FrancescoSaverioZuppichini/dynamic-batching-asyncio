from typing import Union, Dict, Any, List
from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
from logger import logger


class InferenceData(BaseModel):
    uid: str
    model_id: str
    data: Dict[str, Any]


class BatchedInferenceData(BaseModel):
    batch: List[InferenceData]


app = FastAPI()

result = [0]

@app.post("/inference")
async def inference(batch: List[InferenceData]):
    logger.info("Received batch, doing work....")
    await asyncio.sleep(1)
    result[0] += 1
    results = [{"uid": item.uid, "data": {"result": result[0]}} for item in batch]
    logger.info("Done!")
    return results
