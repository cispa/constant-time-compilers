

#include <stdint.h>

uint8_t checkstr(char* expected, char* actual, int len) {
    uint32_t x = 0;
    while (x < len) {
        if (expected[x] != actual[x]) return 0;
        x++;
    }
    return 1;
}