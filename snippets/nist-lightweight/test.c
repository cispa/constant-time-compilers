#include "crypto_aead.h"
#include "crypto_hash.h"
#include "api.h"

/**
 *
*/
void test_aead_encrypt(unsigned char *c, unsigned long long *clen, unsigned char *m, unsigned long long mlen , unsigned char *ad, unsigned long long adlen, unsigned char *nsec, unsigned char *npub, unsigned char *k) {
    crypto_aead_encrypt(c, clen, m, mlen, ad, adlen, nsec, npub, k);
    crypto_aead_decrypt(m, mlen, nsec, c, clen, ad, adlen, npub, k);
}