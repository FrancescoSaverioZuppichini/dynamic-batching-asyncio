
build:
	python -m grpc_tools.protoc -I src --python_out=src --pyi_out=src --grpc_python_out=src src/worker.proto 