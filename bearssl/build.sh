#!/bin/bash
git clone https://www.bearssl.org/git/BearSSL bearssl-git
pushd bearssl-git
git checkout 79c060eea3eea1257797f15ea1608a9a9923aa6f # newest state at time of development
if [ -f Makefile ]; then
    make clean
fi
./Configure
popd
python3 ./build_bearssl.py