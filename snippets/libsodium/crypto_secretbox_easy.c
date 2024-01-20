#include "sodium.h"

void test_crypto_secretbox_easy(const unsigned char* key, const unsigned char* plain){
    sodium_init();
    unsigned char c[56];
    const unsigned char n[24] = {0};
    crypto_secretbox_easy(c,plain,32,n,key);
}