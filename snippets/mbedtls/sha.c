#include "mbedtls/sha256.h"
#include "mbedtls/sha512.h"

/**
 * PLAIN: 64 bytes
*/
void test_sha_256(unsigned char* plain) {
    unsigned char digest[64];
    mbedtls_sha256_context ctx;
    mbedtls_sha256_init(&ctx);
    mbedtls_sha256_update(&ctx,plain,64);
    mbedtls_sha256_update(&ctx,plain,64);
    mbedtls_sha256_finish(&ctx, digest);
    mbedtls_sha256_free(&ctx);
}

/**
 * PLAIN: 64 bytes
*/
void test_sha_512(unsigned char* plain) {
    unsigned char digest[64];
    mbedtls_sha512_context ctx;
    mbedtls_sha512_init(&ctx);
    mbedtls_sha512_update(&ctx,plain,64);
    mbedtls_sha512_update(&ctx,plain,64);
    mbedtls_sha512_finish(&ctx, digest);
    mbedtls_sha512_free(&ctx);
}