#include "bearssl.h"

/**
 * PLAIN: 64 bytes
*/
void test_sha_256(unsigned char* plain) {
    br_sha256_context csha256;
    unsigned char digest[64];
    br_sha256_init(&csha256);
    br_sha256_update(&csha256, plain, 64);
    br_sha256_update(&csha256, plain, 64);
    br_sha256_out(&csha256, (void*) digest);
}

/**
 * PLAIN: 64 bytes
*/
void test_sha_512(unsigned char* plain) {
    br_sha512_context csha512;
    unsigned char digest[64];
    br_sha512_init(&csha512);
    br_sha512_update(&csha512, plain, 64);
    br_sha512_update(&csha512, plain, 64);
    br_sha512_out(&csha512, (void*) digest);
}