#!/bin/bash
git clone git://git.openssl.org/openssl.git openssl-git
pushd openssl-git
git checkout 2cf4e90eaaf7402bf038b158dbdacd0a15561fb7 # 3.1.1, newest stable at time of development
if [ -f Makefile ]; then
    make distclean
fi
./Configure no-shared
popd
python3 ./build_openssl.py
mv precompiled precompiled_asm
pushd openssl-git
make distclean
./Configure no-shared no-asm
popd
python3 ./build_openssl.py
mv precompiled precompiled_noasm
pushd openssl-git
make distclean
./Configure no-shared no-asm -DOPENSSL_AES_CONST_TIME
popd
python3 ./build_openssl.py
mv precompiled precompiled_noasm_ct

