#include "sodium.h"

void test_hmac_sha(const unsigned char* key, const unsigned char* plain){
    sodium_init();
    unsigned char hash[64];
    crypto_auth_hmacsha512(hash, plain, 32, key);
}