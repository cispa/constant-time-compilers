#include "sodium.h"

void test_chacha20(void* key, const unsigned char* plain){
    unsigned char output[64];
    const unsigned char nonce[12] = {0};
    crypto_stream_chacha20_xor(output,plain,64,nonce, key);
}

void test_chacha20_ietf(void* key, const unsigned char* plain){
    unsigned char output[64];
    const unsigned char nonce[12] = {0};
    crypto_stream_chacha20_ietf_xor(output,plain,64,nonce, key);
}