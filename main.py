from typing import Union, Dict, Any, Optional
from fastapi import FastAPI
from pydantic import BaseModel
import asyncio

# list of known workers
worker_url = "http://localhost:8001/inference"

from load_balancer import LoadBalancer


class InferenceData(BaseModel):
    model_id: str
    data: Dict[str, Any]


app = FastAPI()
load_balancer = LoadBalancer(max_batch_size=8, batch_timeout_ms=200, worker_url=worker_url)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(load_balancer.consumer())

@app.on_event("shutdown")
async def startup_event():
    load_balancer.shutdown()


@app.post("/inference")
async def inference(data: InferenceData):
    response = await load_balancer.send(dict(data))
    return response
