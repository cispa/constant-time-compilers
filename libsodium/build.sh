#!/bin/bash
wget -nc https://download.libsodium.org/libsodium/releases/libsodium-1.0.19-stable.tar.gz
tar -xzf libsodium-1.0.19-stable.tar.gz

python3 ./build_libsodium.py