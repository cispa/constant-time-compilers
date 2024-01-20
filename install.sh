#!/bin/bash
# Check if script is executed on an Ubuntu installation 
if [[ $(uname -v | grep -c Ubuntu) -eq "0" ]]; then
    read -p "It seems you are not running Ubuntu. Install anyway? (yN) " installAnyway

    case $installAnyway in
    y) echo "Starting installation on non-Ubuntu system." ;;
    *) echo "Terminating."; exit -1 ;;
    esac
fi

# Update repositories
sudo apt-get update -y
sudo apt-get upgrade -y

# Install basic tools and libraries
sudo apt-get install -y --autoremove  libssl-dev git curl pypy3 pypy3-dev python3 python3-setuptools python3-pip python3-virtualenv automake build-essential gcc-multilib g++ cmake make clang python3 python3-pip valgrind libc6-dbg locales time
sudo locale-gen en_US.UTF-8
sudo update-locale
sudo pip3 install pathos

# Install rust compiler toolchain
# curl -L https://sh.rustup.rs -sSf | sh -s -- -y -c rust-src
# source "$HOME/.cargo/env"

# Download and install TinyC compiler
git clone https://repo.or.cz/tinycc.git compilers/tinycc
pushd compilers/tinycc
./configure
make
sudo make install
popd

# Download and install Intel C compiler
curl https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS.PUB | gpg --dearmor | sudo tee /usr/share/keyrings/oneapi-archive-keyring.gpg > /dev/null
echo "deb [signed-by=/usr/share/keyrings/oneapi-archive-keyring.gpg] https://apt.repos.intel.com/oneapi all main" | sudo tee /etc/apt/sources.list.d/oneAPI.list
sudo apt-get update
sudo apt-get install -y intel-oneapi-compiler-dpcpp-cpp


# Download and install AMD Optimizing C Compiler
mkdir -p compilers/aocc
if [ ! -f "compilers/aocc/aocc.deb" ]; then
    curl -o compilers/aocc/aocc.deb https://download.amd.com/developer/eula/aocc-compiler/aocc-compiler-4.0.0_1_amd64.deb
    sudo dpkg -G -i compilers/aocc/aocc.deb
fi

# Download and install Compcert C Compiler
sudo apt install -y opam
opam init --yes
opam switch --yes create 4.13.1     # Use OCaml version 4.13.1 (for example)
eval $(opam env)
opam install --yes coq=8.13.2       # Use Coq version 8.13.2 (for example)
opam install --yes menhir
git clone https://github.com/AbsInt/CompCert.git compilers/compcert
pushd compilers/compcert
./configure x86_64-linux
make -j 
sudo make install
popd

# Download and install zig cc C compiler
sudo snap install zig --classic --beta

# Setup haybale-pitchfork
#pushd checkers/pitchfork
#cargo build -r
#mkdir -p bin
#cp target/release/pitchfork bin
#popd

# Setup dudect
# mkdir -p checkers/dudect
# pushd checkers/dudect
# if [ ! -f "dudect.h" ]; then
#     curl -L -o dudect.h https://raw.githubusercontent.com/oreparaz/dudect/master/src/dudect.h
# fi
# popd

# Setup ct-grind
# No setup needed as this is now a part of valgrind
# mkdir -p checkers/ct-grind
# pushd checkers/ct-grind
# if [ ! -d ".git" ]; then
#     git clone https://github.com/jedisct1/ctgrind.git .
# fi
# ./autogen.sh
# ./configure
# make
# popd

# Setup DATA
mkdir -p checkers/DATA
pushd checkers/DATA
if [ ! -d "DATA-git/.git" ]; then
    git clone https://github.com/Fraunhofer-AISEC/DATA.git DATA-git
    pushd DATA-git
    make setup
    popd
fi
popd

# Setup Pitchfork/Angr
mkdir -p checkers/pitchfork-angr
pushd checkers/pitchfork-angr
if [ ! -d "pitchfork-angr/.git" ]; then
    git clone https://github.com/PLSysSec/pitchfork-angr pitchfork-angr
    git clone https://github.com/cdisselkoen/angr -b more-hooks angr-git
    pypy3 -m venv venv
    source venv/bin/activate
    pip3 install ailment ana archinfo backcall bitstring cachetools capstone cffi claripy cle cooldict decorator dpkt future gitdb2 GitPython greenlet idalink ipdb ipython ipython-genutils itanium-demangler jedi mulpyplexer networkx parso pefile pexpect pickleshare plumbum progressbar prompt-toolkit protobuf psutil ptyprocess pycparser pyelftools Pygments PySMT pyvex readline rpyc six smmap2 sortedcontainers traitlets unicorn wcwidth z3-solver 
    pip3 install angr==8.19.4.5 # This installs angr with all of its dependencies
    pip3 uninstall angr -y    # This removes angr but not its dependencies
    pushd ./angr-git
    python3 ./setup.py build
    python3 ./setup.py install
    popd
    deactivate
fi
popd

# Setup binsec/rel
# mkdir -p checkers/binsec-rel
# pushd checkers/binsec-rel
# if [ ! -d ".git" ]; then
#     git clone https://github.com/binsec/Rel.git .
# fi
# if [ ! -f "binsec" ]; then
#     opam init -a
#     OPAMCONFIRMLEVEL=yes make switch -B
#     eval $(opam env)
#     OPAMCONFIRMLEVEL=yes make
#     ln $(readlink -f _build/install/default/bin/binsec) binsec
#     chmod ugo+x binsec
# fi
# if [ ! -f "libsym.a" ]; then
#     curl -L -o sym.c https://github.com/binsec/rel_bench/raw/main/properties_vs_compilers/ct/src/__libsym__/sym.c
#     curl -L -o sym.h https://github.com/binsec/rel_bench/raw/main/properties_vs_compilers/ct/src/__libsym__/sym.h
#     gcc -c -static -fno-stack-protector -o sym.o sym.c
#     ar rcs libsym.a sym.o
#     rm sym.o
# fi
# popd

# Setup OpenSSL
pushd openssl
./build.sh
popd

# Setup BearSSL
pushd bearssl
./build.sh
popd

echo "Successfully installed CTCCP toolchain!"
