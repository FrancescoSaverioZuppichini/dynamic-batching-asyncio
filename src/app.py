from fastapi import FastAPI
from data_models import InferenceRequest
from model import Model
from utils import b64image_to_pil

my_model = Model()

app = FastAPI()

@app.post("/inference")
async def inference(req: InferenceRequest):
    image = b64image_to_pil(req.data.image)
    preds = my_model.inference([image])
    return {"pred" : preds[0]}
