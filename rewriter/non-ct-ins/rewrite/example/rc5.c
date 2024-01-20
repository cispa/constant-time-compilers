#include <stdio.h>

#   define RC5_32_INT unsigned int
#   define RC5_16_ROUNDS   16

typedef struct rc5_key_st {
    /* Number of rounds */
    int rounds;
    RC5_32_INT data[2 * (RC5_16_ROUNDS + 1)];
} RC5_32_KEY;

#define RC5_32_MASK     0xffffffffL

#define RC5_32_P        0xB7E15163L
#define RC5_32_Q        0x9E3779B9L

#  define ROTATE_l32(a,n)       ({ register unsigned int ret;   \
                                        asm ("roll %%cl,%0"     \
                                                : "=r"(ret)     \
                                                : "c"(n),"0"((unsigned int)(a)) \
                                                : "cc");        \
                                        ret;                    \
                                })
#  define ROTATE_r32(a,n)       ({ register unsigned int ret;   \
                                        asm ("rorl %%cl,%0"     \
                                                : "=r"(ret)     \
                                                : "c"(n),"0"((unsigned int)(a)) \
                                                : "cc");        \
                                        ret;                    \
                                })

#define E_RC5_32(a,b,s,n) \
        a^=b; \
        a=ROTATE_l32(a,b); \
        a+=s[n]; \
        a&=RC5_32_MASK; \
        b^=a; \
        b=ROTATE_l32(b,a); \
        b+=s[n+1]; \
        b&=RC5_32_MASK;

#define D_RC5_32(a,b,s,n) \
        b-=s[n+1]; \
        b&=RC5_32_MASK; \
        b=ROTATE_r32(b,a); \
        b^=a; \
        a-=s[n]; \
        a&=RC5_32_MASK; \
        a=ROTATE_r32(a,b); \
        a^=b;



void RC5_32_encrypt(unsigned long *d, RC5_32_KEY *key)
{
    RC5_32_INT a, b, *s;

    s = key->data;

    a = d[0] + s[0];
    b = d[1] + s[1];
    E_RC5_32(a, b, s, 2);
    E_RC5_32(a, b, s, 4);
    E_RC5_32(a, b, s, 6);
    E_RC5_32(a, b, s, 8);
    E_RC5_32(a, b, s, 10);
    E_RC5_32(a, b, s, 12);
    E_RC5_32(a, b, s, 14);
    E_RC5_32(a, b, s, 16);
    if (key->rounds == 12) {
        E_RC5_32(a, b, s, 18);
        E_RC5_32(a, b, s, 20);
        E_RC5_32(a, b, s, 22);
        E_RC5_32(a, b, s, 24);
    } else if (key->rounds == 16) {
        /* Do a full expansion to avoid a jump */
        E_RC5_32(a, b, s, 18);
        E_RC5_32(a, b, s, 20);
        E_RC5_32(a, b, s, 22);
        E_RC5_32(a, b, s, 24);
        E_RC5_32(a, b, s, 26);
        E_RC5_32(a, b, s, 28);
        E_RC5_32(a, b, s, 30);
        E_RC5_32(a, b, s, 32);
    }
    d[0] = a;
    d[1] = b;
}

void RC5_32_decrypt(unsigned long *d, RC5_32_KEY *key)
{
    RC5_32_INT a, b, *s;

    s = key->data;

    a = d[0];
    b = d[1];
    if (key->rounds == 16) {
        D_RC5_32(a, b, s, 32);
        D_RC5_32(a, b, s, 30);
        D_RC5_32(a, b, s, 28);
        D_RC5_32(a, b, s, 26);
        /* Do a full expansion to avoid a jump */
        D_RC5_32(a, b, s, 24);
        D_RC5_32(a, b, s, 22);
        D_RC5_32(a, b, s, 20);
        D_RC5_32(a, b, s, 18);
    } else if (key->rounds == 12) {
        D_RC5_32(a, b, s, 24);
        D_RC5_32(a, b, s, 22);
        D_RC5_32(a, b, s, 20);
        D_RC5_32(a, b, s, 18);
    }
    D_RC5_32(a, b, s, 16);
    D_RC5_32(a, b, s, 14);
    D_RC5_32(a, b, s, 12);
    D_RC5_32(a, b, s, 10);
    D_RC5_32(a, b, s, 8);
    D_RC5_32(a, b, s, 6);
    D_RC5_32(a, b, s, 4);
    D_RC5_32(a, b, s, 2);
    d[0] = a - s[0];
    d[1] = b - s[1];
}

int main(int argc, char** argv) {

  if (argc != 2) {
    printf("Provide <key-file> as argument\n");
    return -1;
  }

  FILE* f = fopen(argv[1], "r");
  if (!f) {
    perror("Unable to open file");
    return -2;
  }

  RC5_32_KEY key;
  key.rounds = 16;
  unsigned int keydata[34] = {0};
  unsigned long in[2] = {0};

  // Read the array from the file
  size_t elements_read = fread(keydata, sizeof(unsigned int), 34, f);

  RC5_32_encrypt(in,&key);
  RC5_32_decrypt(in,&key);

  fclose(f);
}


  