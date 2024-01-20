

#include <stdint.h>

uint32_t divisible(uint32_t x, uint32_t y) {
    if (x == 0 || y == 0) return 1;
    if (x < y) return 0;
    return divisible(x - y, y);
}