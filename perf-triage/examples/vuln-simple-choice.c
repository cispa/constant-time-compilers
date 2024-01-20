#define TEST_RUNS 1e4
#include "checker_random.h"
#include <time.h>
#include <valgrind/memcheck.h>
#include <stdint.h>

uint32_t choice(uint32_t cond, uint32_t x, uint32_t y) {
    if (cond) return x;
    return y;
}
int main() {
struct timespec curr_time;
clock_gettime(CLOCK_MONOTONIC, &curr_time);
for (uint64_t i = 0; i < TEST_RUNS; i++) {
srand(curr_time.tv_nsec);
uint32_t arg_0 = 0;
uint32_t arg_1 = 0;
uint32_t arg_2 = 0;
checker_fill_unconstrained((void*) &arg_0, 1, sizeof(uint32_t));
VALGRIND_MAKE_MEM_UNDEFINED((void*) &arg_0, sizeof(arg_0));
checker_fill_unconstrained((void*) &arg_1, 1, sizeof(uint32_t));
VALGRIND_MAKE_MEM_UNDEFINED((void*) &arg_1, sizeof(arg_1));
checker_fill_unconstrained((void*) &arg_2, 1, sizeof(uint32_t));
VALGRIND_MAKE_MEM_UNDEFINED((void*) &arg_2, sizeof(arg_2));
choice(arg_0, arg_1, arg_2);
}
return 0;
}

