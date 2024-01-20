#include "stdlib.c"

static char s1[2] = {0,1};
static char s2[2] = {1,0};

void entry(size_t arg1, size_t arg2)
{
    int bit;
    int acc = 0;
    for (size_t i = 0; i < 64; i++)
    {
        bit = (arg2>>i) & 0x1;
        if(bit){
            acc += s1[bit];
        }else{
            acc += s2[bit];
        }
    }
}