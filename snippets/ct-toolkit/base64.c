#include "cttk.h"

/*
* This leaks the location of whitespace but that is okay as it it not considered secret
*/
void test_base64(char *dst, size_t dst_len,void *src, size_t src_len){
    cttk_bintob64_gen(dst, dst_len, (const void *) src, src_len,CTTK_B64DEC_NO_PAD);
    cttk_b64tobin_gen(src, src_len, dst, dst_len, NULL, CTTK_B64DEC_NO_PAD);
}