#include "wolfssl/options.h"
#include "wolfssl/wolfcrypt/camellia.h"

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
    Camellia camellia;
    wc_CamelliaSetKey(&camellia, key, CAMELLIA_BLOCK_SIZE, iv);
    wc_CamelliaCbcEncrypt(&camellia, output, plain, 32);
}
