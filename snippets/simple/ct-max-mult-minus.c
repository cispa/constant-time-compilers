

#include <stdint.h>

uint32_t max(uint32_t x, uint32_t y) {
    uint8_t sel = (x > y);
    return sel * x + (1 - sel) * y; 
}