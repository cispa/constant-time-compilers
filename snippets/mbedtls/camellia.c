#include "mbedtls/camellia.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

/**
 * KEY: 256 bits = 32 bytes
 * IV: 128 bits = 16 bytes
 * PLAIN: 32 bytes
*/
void test_camellia_cbc(void* key, void* iv, const unsigned char* plain) {
    unsigned char output[64];
    mbedtls_camellia_context ctx;
    mbedtls_camellia_init(&ctx);
    mbedtls_camellia_setkey_enc(&ctx, key, 256);
    mbedtls_camellia_crypt_cbc( &ctx, MBEDTLS_CAMELLIA_ENCRYPT, 16, iv, plain, output );
}
