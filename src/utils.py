import base64
from io import BytesIO

from PIL import Image


def b64image_to_pil(image: bytes) -> Image.Image:
    return Image.open(BytesIO(base64.b64decode(image)))
