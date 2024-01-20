#include "sodium.h"

void test_sha(const unsigned char* key, const unsigned char* plain){
    sodium_init();
    unsigned char hash[32];
    crypto_hash_sha256(hash,plain,32);
}