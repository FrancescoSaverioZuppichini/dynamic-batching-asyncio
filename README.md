# Dynamic Batching with FastAPI and Asyncio

Minimum example for creating a http server with dynamic batching using FastAPI and Asyncio

## Getting Started

Run the worker

```
cd src && uvicorn app:app --reload --loop uvloop
```

Run the worker

```
cd src && uvicorn worker:app --port 8001 --loop uvloop --reload 
```

Run the benchmark

```
python benchmark.py --num_threads=8 --num_requests=128 --sleep 0.05
```