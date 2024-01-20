#include "cttk.h"

/*
* This leaks the location of whitespace but that is okay as it it not considered secret
*/
void test_hex(char *dst, size_t dst_len,const void *src, size_t src_len){
    cttk_bintohex_gen(dst, dst_len, src, src_len, 0);
    cttk_hextobin_gen(src, src_len, dst, dst_len, NULL, 0);
}