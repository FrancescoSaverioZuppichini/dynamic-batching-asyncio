import base64
from io import BytesIO

import requests
from PIL import Image

URL = "http://127.0.0.1:8000"

image = Image.open("../examples/cat.jpeg")
buffered = BytesIO()
image.save(buffered, format="JPEG")
img_str = base64.b64encode(buffered.getvalue())

res = requests.post(
    f"{URL}/inference", json={"data": {"image": img_str.decode("utf-8")}}
)
print(res.json())
