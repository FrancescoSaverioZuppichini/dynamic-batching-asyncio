from typing import Union, Dict, Any, Optional
from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
import aiohttp

# list of known workers
worker_url = "http://localhost:8001/inference"

client = aiohttp.ClientSession()

class InferenceData(BaseModel):
    model_id: str
    data: Dict[str, Any]


app = FastAPI()


@app.post("/inference")
async def inference(data: InferenceData):
    async with client.post(
        worker_url, json=data.dict(), timeout=5
    ) as result:
        result.raise_for_status()
        response = await result.json()
        return response
