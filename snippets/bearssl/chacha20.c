#include "bearssl.h"

void test_chacha20(void* key, const unsigned char* plain){
    unsigned char output[64];
    const unsigned char nonce[12] = {0};
    br_chacha20_ct_run(key,nonce, 0, plain, 64);
}