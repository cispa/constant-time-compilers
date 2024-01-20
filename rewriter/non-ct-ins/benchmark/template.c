#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <fenv.h>

#include "cacheutils.h"

#define LOOP 10

#define REP2(x) x x
#define REP4(x) REP2(x) REP2(x)
#define REP8(x) REP4(x) REP4(x)
#define REP10(x) REP8(x) REP2(x)


// Example functions from 
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

static uint64_t res;

int main(int argc, char **argv)
{

    if (argc < 2)
    {
        printf("usage: %s <cpu> <reps>\n", argv[0]);
        return 1;
    }

    int cpu = atoi(argv[1]);
    int reps = atoi(argv[2]);

    // Create log files
    FILE *fp_static = fopen("./data/static.csv", "a");
    FILE *fp_rand = fopen("./data/randomized.csv", "a");

    // Disable floating point exception
    feraiseexcept(FE_ALL_EXCEPT);

    // Init key structs for test
    uint64_t a,b;

    int randomized = 0;

    for (size_t rep = 0; rep < reps; rep++)
    {
        if(rep%(reps/100) == 0)
            printf("Run %ld\n", rep);

        // Randomly decide class
        randomized = rdtsc() & 1;
        if (randomized)
        {
            // Randomized
            a = rdtsc();
            b = rdtsc();
            
        }
        else
        {
            // Static
            a = 1;
            b = 1;
        }

        uint64_t start,end;
        
        start = rdtsc();
        // Insert operation to benchmark here
        ROTATE_r32(a,b);
        end = rdtsc();

        if (randomized)
        {
            fprintf(fp_rand, "%ld\n", end-start);
        }
        else
        {
            fprintf(fp_static, "%ld\n", end-start);
        }
    }
}