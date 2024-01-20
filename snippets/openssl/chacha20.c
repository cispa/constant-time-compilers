#include "openssl/evp.h"

/**
 * KEY: 256 bits = 32 bytes
 * IV: 128 bits = 16 bytes
 * PLAIN: 32 bytes
*/
void test_chacha20(unsigned char* key, unsigned char* iv, unsigned char* plain) {
    int plain_len = 32;
    int enc_len = 0;
    unsigned char enc_data[64] = {0};
    // Perform encryption
    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    EVP_EncryptInit(ctx, EVP_chacha20(), key, iv);
    EVP_EncryptUpdate(ctx, enc_data, &enc_len, plain, 32);
    EVP_EncryptFinal(ctx, enc_data + enc_len, &enc_len);
    EVP_CIPHER_CTX_free(ctx);
}

