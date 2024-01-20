#include <stdlib.h>
#include <time.h>
#include <valgrind/memcheck.h>
#include "../../../../ct-toolkit/cttk.h"

void fill_rand(char array[], int size) {
    for (int i = 0; i < size; i++) {
        array[i] = rand()&255;
    }
}


int main() {
  srand((unsigned int)time(NULL));

  char src[32] = {0};
  char dst[64] = {0};

  fill_rand(src,32);
  VALGRIND_MAKE_MEM_UNDEFINED(src, 32);
  cttk_bintob64_gen(dst, 64, (const void *) src, 32,CTTK_B64DEC_NO_PAD);
  cttk_b64tobin_gen(src, 32, dst, 64, NULL, CTTK_B64DEC_NO_PAD);
}