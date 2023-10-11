#!/bin/bash

# ref. https://github.com/mtconnect/cppagent/blob/main/.github/workflows/build.yml

sudo apt-get install build-essential python3 python3-pip git cmake ruby rake autoconf
python3 -m pip install conan

source ~/.profile
conan profile detect -f

git clone https://github.com/mtconnect/cppagent.git

cd cppagent
mkdir build

conan create . -pr conan/profiles/gcc --build=missing \
-o cpack=True \
-o cpack_destination=build \
-o cpack_name=dist \
-o cpack_generator=TGZ