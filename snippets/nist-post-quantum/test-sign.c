#include "api.h"

/*
* TODO: Call this function before without tracing to generate a nice keypair
*/
//int crypto_sign_keypair(unsigned char *pk, unsigned char *sk);

void test_sign(unsigned char *sm, unsigned long long *smlen,const unsigned char *msg, unsigned long long len,const unsigned char *sk){
    crypto_sign(sm, smlen,msg,len,sk);
}