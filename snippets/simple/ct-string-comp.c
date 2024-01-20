
#include <stdint.h>

uint8_t checkstr(char* expected, char* actual, uint32_t len) {
    uint32_t x = 0;
    uint8_t result = 1;
    while (x < len) {
        result &= (expected[x] == actual[x]);
        x++;
    }
    return result;
}