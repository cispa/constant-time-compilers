

#include <stdint.h>

uint32_t LUT[] = {13, 37, 42, 82, 79, 66, 69, 82, 84, 0};

uint32_t lookup(uint32_t index) {
    return LUT[index];
}