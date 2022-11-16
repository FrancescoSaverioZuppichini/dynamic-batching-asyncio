import asyncio
import base64
from io import BytesIO

import grpc
from PIL import Image

from worker_pb2 import InferenceRequest
from worker_pb2_grpc import WorkerStub

image = Image.open("../examples/cat.jpeg")
buffered = BytesIO()
image.save(buffered, format="JPEG")
img_str = base64.b64encode(buffered.getvalue())


async def main():
    async with grpc.aio.insecure_channel("[::]:50052 ") as channel:
        stub = WorkerStub(channel)
        res = await stub.inference(
            InferenceRequest(data=InferenceRequest.InferenceData(image=img_str))
        )
        print(res)


if __name__ == "__main__":
    asyncio.run(main())
