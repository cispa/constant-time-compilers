
#include <limits.h>
#include <stdint.h>

uint64_t power(uint32_t base, uint32_t exponent) {
    uint64_t result = 1;
    for (int i = 0; i < 32; i++) {
        result *= result;
        if (exponent >> (31 - i) & 1) result *= base;
    }
    return result;
}