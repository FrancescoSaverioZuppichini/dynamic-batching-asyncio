import asyncio
from typing import Any, Dict, Optional, Union

import aiohttp
import grpc
from fastapi import FastAPI
from pydantic import BaseModel

from data_models import InferenceRequest
from worker_pb2 import InferenceRequest as GRPCInferenceRequest
from worker_pb2_grpc import WorkerStub

worker_grpc_url = "[::]:50052"  # ipv6

client = aiohttp.ClientSession()


app = FastAPI()

@app.on_event("startup")
async def startup_event():
    app.grpc_channel = grpc.aio.insecure_channel("[::]:50052 ")
    app.stub = WorkerStub(app.grpc_channel)

@app.on_event("shutdown")
async def startup_event():
    app.grpc_channel.close()

@app.post("/inference")
async def inference(req: InferenceRequest):
    # async with grpc.aio.insecure_channel(worker_grpc_url) as channel:
        # stub = WorkerStub(channel)
        response = await app.stub.inference(
            GRPCInferenceRequest(
                data=GRPCInferenceRequest.InferenceData(image=req.data.image)
            )
        )
        return {"pred" : response.pred}
