#include "sodium.h"

void test_crypto_generichash(const unsigned char* key, const unsigned char* plain){
    sodium_init();
    unsigned char hash[32];
    const unsigned char n[24] = {0};
    crypto_generichash(hash,32,plain,32,key,32);
}