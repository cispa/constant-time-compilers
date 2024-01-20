#!/bin/bash
wget -nc https://csrc.nist.gov/CSRC/media/Projects/lightweight-cryptography/documents/finalist-round/updated-submissions/ascon.zip
unzip -o ascon.zip
# rm ascon.zip

wget -nc https://csrc.nist.gov/CSRC/media/Projects/lightweight-cryptography/documents/finalist-round/updated-submissions/elephant.zip
unzip -o elephant.zip
# rm elephant.zip

wget -nc https://csrc.nist.gov/CSRC/media/Projects/lightweight-cryptography/documents/finalist-round/updated-submissions/gift-cofb.zip
unzip -o gift-cofb.zip
# rm gift-cofb.zip

wget -nc https://csrc.nist.gov/CSRC/media/Projects/lightweight-cryptography/documents/finalist-round/updated-submissions/grain-128aead.zip
unzip -o grain-128aead.zip
# rm grain-128aead.zip

wget -nc https://csrc.nist.gov/CSRC/media/Projects/lightweight-cryptography/documents/finalist-round/updated-submissions/isap.zip
unzip -o isap.zip
# rm isap.zip

wget -nc  https://csrc.nist.gov/CSRC/media/Projects/lightweight-cryptography/documents/finalist-round/updated-submissions/photon-beetle.zip
unzip -o photon-beetle.zip
# rm photon-beetle.zip

wget -nc https://csrc.nist.gov/CSRC/media/Projects/lightweight-cryptography/documents/finalist-round/updated-submissions/romulus.zip
unzip -o romulus.zip
# rm romulus.zip

wget -nc https://csrc.nist.gov/CSRC/media/Projects/lightweight-cryptography/documents/finalist-round/updated-submissions/sparkle.zip
unzip -o sparkle.zip
# rm sparkle.zip

wget -nc https://csrc.nist.gov/CSRC/media/Projects/lightweight-cryptography/documents/finalist-round/updated-submissions/tinyjambu.zip
unzip -o tinyjambu.zip
# rm tinyjambu.zip

wget -nc https://csrc.nist.gov/CSRC/media/Projects/lightweight-cryptography/documents/finalist-round/updated-submissions/xoodyak.zip
unzip -o xoodyak.zip
# rm xoodyak.zip

python3 ./build_nist_lightweight.py
