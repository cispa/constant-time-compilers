

#include <limits.h>
#include <stdint.h>

uint64_t power(uint32_t base, uint32_t exponent) {
    uint64_t result = 1;
    for (int i = 0; i < 32; i++) {
        uint8_t x = exponent >> (31 - i) & 1;
        result *= result * (x * base + (1 - x));
    }
    return result;
}