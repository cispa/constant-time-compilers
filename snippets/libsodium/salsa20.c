#include "sodium.h"

void test_salsa20(void* key, const unsigned char* plain){
    unsigned char output[64];
    const unsigned char nonce[8] = {0};
    crypto_stream_salsa20_xor(output,plain,64,nonce,key);
}
