import requests

res = requests.post(
    "http://localhost:8000/inference", json={"model_id": "asd", "data": {}}
)
print(res.text)