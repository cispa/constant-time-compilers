#include "mbedtls/poly1305.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

/**
 * KEY: 256 bits = 32 bytes
 * IV: 128 bits = 16 bytes
 * PLAIN: 32 bytes
*/
void test_poly1305(void* key, const unsigned char* plain) {
    unsigned char output[64];
    const unsigned char mac[16] = {0};
    mbedtls_poly1305_context ctx;
    mbedtls_poly1305_init(&ctx);
    mbedtls_poly1305_starts(&ctx, key);
    mbedtls_poly1305_update(&ctx, plain, 64);
    mbedtls_poly1305_finish(&ctx, mac);
    mbedtls_poly1305_mac(key,plain,64,mac);
}
