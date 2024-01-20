#include "mbedtls/aria.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

/**
 * KEY: 256 bits = 32 bytes
 * IV: 128 bits = 16 bytes
 * PLAIN: 32 bytes
*/
void test_aria_cbc(void* key, void* iv, const unsigned char* plain) {
    unsigned char output[64];
    mbedtls_aria_context ctx;
    mbedtls_aria_init(&ctx);
    mbedtls_aria_setkey_enc(&ctx, key, 256);
    mbedtls_aria_crypt_cbc( &ctx, MBEDTLS_ARIA_ENCRYPT, 16, iv, plain, output );
}
