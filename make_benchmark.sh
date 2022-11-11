# !/bin/bash

python benchmark.py --num_threads=1 --num_requests=32 --sleep 0.05
python benchmark.py --num_threads=2 --num_requests=64 --sleep 0.05
python benchmark.py --num_threads=4 --num_requests=128 --sleep 0.05
python benchmark.py --num_threads=8 --num_requests=512 --sleep 0.05
python benchmark.py --num_threads=16 --num_requests=1024 --sleep 0.05
python benchmark.py --num_threads=32 --num_requests=2048 --sleep 0.05