#!/bin/sh

# Put protobuf executable 'protoc' in same directory
# https://protobuf.dev/getting-started/pythontutorial/#compiling-protocol-buffers
./protoc -I=. --python_out=. transition.proto --include_imports --descriptor_set_out=descr.txt
