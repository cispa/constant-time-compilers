#include "mbedtls/aes.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

/**
 * KEY: 256 bits = 32 bytes
 * IV: 128 bits = 16 bytes
 * PLAIN: 32 bytes
*/
void test_aes_cbc(void* key, void* iv, const unsigned char* plain) {
    unsigned char output[64];
    mbedtls_aes_context ctx;
    mbedtls_aes_init(&ctx);
    mbedtls_aes_setkey_enc(&ctx, key, 256);
    mbedtls_aes_crypt_cbc( &ctx, MBEDTLS_AES_ENCRYPT, 48, iv, plain, output );
}
