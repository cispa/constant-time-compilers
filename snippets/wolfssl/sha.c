#include "wolfssl/options.h"
#include "wolfssl/wolfcrypt/sha256.h"
#include "wolfssl/wolfcrypt/sha512.h"

/**
 * PLAIN: 64 bytes
*/
void test_sha_256(unsigned char* plain) {
    unsigned char digest[64];
    wc_Sha256 sha;
    wc_InitSha256(&sha);
    wc_Sha256Update(&sha,plain,32);
    wc_Sha256Final(&sha,digest);
}

/**
 * PLAIN: 64 bytes
*/
void test_sha_512(unsigned char* plain) {
    unsigned char digest[64];
    wc_Sha512 sha;
    wc_InitSha512(&sha);
    wc_Sha512Update(&sha,plain,32);
    wc_Sha512Final(&sha,digest);
}