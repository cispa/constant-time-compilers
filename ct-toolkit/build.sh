#!/bin/bash
git clone https://github.com/pornin/CTTK.git ct-toolkit-git
pushd ct-toolkit-git
git checkout 1d59202 # newest state at time of development
popd

python3 ./build_ct_toolkit.py
