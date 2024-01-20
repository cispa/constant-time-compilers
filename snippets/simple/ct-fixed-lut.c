
#include <stdint.h>

uint32_t LUT[] = {13, 37, 42, 82, 79, 66, 69, 82, 84, 0};

uint32_t lookup(uint32_t index) {
    uint32_t result = 0;

    for (uint32_t i = 0; i < sizeof(LUT) / sizeof(*LUT); i++) {
        result += (!(i ^ index)) * LUT[i];
    }

    return result;
}