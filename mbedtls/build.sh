#!/bin/bash
git clone https://github.com/Mbed-TLS/mbedtls.git mbedtls-git
pushd mbedtls-git
git checkout da0bb9f # newest state at time of development
if [ -f Makefile ]; then
    make clean
fi
popd
python3 ./build_mbedtls.py