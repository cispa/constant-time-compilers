#include "wolfssl/options.h"
#include "wolfssl/wolfcrypt/chacha.h"

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

/**
 * KEY: 256 bits = 32 bytes
 * IV: 12 bytes
 * PLAIN: 64 bytes
*/
void test_chacha20(void* key, const unsigned char* iv, const unsigned char* plain) {
    unsigned char output[64];
    ChaCha chacha;
    wc_Chacha_SetKey(&chacha,key,32);
    wc_Chacha_SetIV(&chacha,iv,0);
    wc_Chacha_Process(&chacha,output,plain,64);
}
