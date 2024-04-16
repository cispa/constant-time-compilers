
#include <stdint.h>

uint32_t complex_choice(uint32_t cond, uint32_t* x, uint32_t* y) {
    if (cond) return 64 / *x;
    return *y;
}