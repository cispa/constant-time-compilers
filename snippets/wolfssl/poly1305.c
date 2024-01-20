#include "wolfssl/options.h"
#include "wolfssl/wolfcrypt/chacha20_poly1305.h"

#include <stdlib.h>
#include <stdio.h>
#include <string.h>


/**
 * KEY: 256 bits = 32 bytes
 * IV: 128 bits = 16 bytes
 * PLAIN: 32 bytes
*/
void test_poly1305(void* key,const char * iv, const unsigned char* plain) {
    unsigned char output[64];
    const unsigned char mac[16] = {0};
    ChaChaPoly_Aead poly;
    wc_ChaCha20Poly1305_Init(&poly,key,iv,CHACHA20_POLY1305_AEAD_ENCRYPT);
    wc_ChaCha20Poly1305_UpdateAad(&poly, plain, 64);
    wc_ChaCha20Poly1305_Final(&poly,mac);
}
