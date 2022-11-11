import asyncio
from typing import Any, Dict, Optional, Union

import aiohttp
from fastapi import FastAPI
from pydantic import BaseModel

from data_models import InferenceRequest

worker_url = "http://localhost:8001/inference"

client = aiohttp.ClientSession()


app = FastAPI()


@app.post("/inference")
async def inference(req: InferenceRequest):
    async with client.post(worker_url, json=req.dict(), timeout=5) as result:
        result.raise_for_status()
        response = await result.json()
        return response
