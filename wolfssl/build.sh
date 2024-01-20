#!/bin/bash
wget -nc https://github.com/wolfSSL/wolfssl/archive/refs/tags/v5.6.3-stable.tar.gz
rm -r wolfssl-stable
mkdir wolfssl-stable
tar -xzf v5.6.3-stable.tar.gz -C wolfssl-stable --strip-components=1

pushd wolfssl-stable
./autogen.sh
popd

python3 ./build_wolfssl.py