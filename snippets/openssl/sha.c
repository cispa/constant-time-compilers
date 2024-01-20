#include "openssl/evp.h"

/**
 * PLAIN: 64 bytes
*/
void test_sha_256(unsigned char* plain) {
    int dig_len = 0;
    unsigned char digest[64];
    EVP_MD_CTX *ctx = EVP_MD_CTX_new();
    EVP_DigestInit(ctx, EVP_sha256());
    EVP_DigestUpdate(ctx, plain, 64);
    EVP_DigestUpdate(ctx, plain, 64);
    EVP_DigestFinal(ctx, digest, &dig_len);
}

/**
 * PLAIN: 64 bytes
*/
void test_sha_512(unsigned char* plain) {
    int dig_len = 0;
    unsigned char digest[64];
    EVP_MD_CTX *ctx = EVP_MD_CTX_new();
    EVP_DigestInit(ctx, EVP_sha512());
    EVP_DigestUpdate(ctx, plain, 64);
    EVP_DigestUpdate(ctx, plain, 64);
    EVP_DigestFinal(ctx, digest, &dig_len);
}