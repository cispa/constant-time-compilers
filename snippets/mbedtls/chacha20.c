#include "mbedtls/chacha20.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

/**
 * KEY: 256 bits = 32 bytes
 * IV: 128 bits = 16 bytes
 * PLAIN: 32 bytes
*/
void test_chacha20(void* key, const unsigned char* plain) {
    unsigned char output[64];
    const unsigned char nonce[12] = {0};
    mbedtls_chacha20_context ctx;
    mbedtls_chacha20_init(&ctx);
    mbedtls_chacha20_setkey(&ctx,key);
    mbedtls_chacha20_starts(&ctx, nonce, 0);
    mbedtls_chacha20_update(&ctx, 64, plain, output);
}
