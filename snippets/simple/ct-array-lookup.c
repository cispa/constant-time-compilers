

#include <stdint.h>

uint32_t lookup(uint32_t *array, uint32_t index, uint32_t length) {
    uint32_t result = 0;
    for (uint32_t i = 0; i < length; i++) {
        result += (!(i ^ index)) * array[i];
    }
    return result;
}