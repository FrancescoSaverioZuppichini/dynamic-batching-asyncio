# Load balancer

Dynamic batching requests for a worker

## Getting Started

Run the load balancer

```
uvicorn main:app --reload --loop uvloop
```

Run the worker

```
uvicorn worker:app --port 8001 --loop uvloop --reload 
```

Run the benchmark

```
python benchmark.py --num_threads=8 --num_requests=128 --sleep 0.05
```