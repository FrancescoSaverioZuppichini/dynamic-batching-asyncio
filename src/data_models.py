from typing import Optional

from pydantic import BaseModel


class InferenceData(BaseModel):
    image: str


class InferenceRequest(BaseModel):
    data: InferenceData
