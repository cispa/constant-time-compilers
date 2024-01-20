#include "wolfssl/options.h"
#include "wolfssl/wolfcrypt/aes.h"

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
    Aes aes;
    wc_AesInit(&aes, NULL, INVALID_DEVID);
    wc_AesSetKey(&aes, key, AES_BLOCK_SIZE, iv, AES_ENCRYPTION);
    wc_AesCbcEncrypt(&aes, output, plain, 32);
}

