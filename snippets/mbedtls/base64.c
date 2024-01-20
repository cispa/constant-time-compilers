
#include "mbedtls/base64.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

/**
 * PLAIN: 64 bytes
*/
void test_base64(const unsigned char* plain) {
    unsigned char output[128];
    size_t len;
    mbedtls_base64_encode(output,128,&len,plain,64);
}
