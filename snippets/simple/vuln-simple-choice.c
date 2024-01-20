

#include <stdint.h>

uint32_t choice(uint32_t cond, uint32_t x, uint32_t y) {
    if (cond) return x;
    return y;
}