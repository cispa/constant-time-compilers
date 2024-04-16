
#include <stdint.h>

uint32_t max(uint32_t x, uint32_t y) {
    volatile uint32_t maximum = x;
    asm volatile (
        "cmpl %[x], %[y]\t\n"
        "cmovae %[x], %[maximum]\t\n"
        : [maximum] "=r" (maximum) : [x] "r" (x), [y] "r" (y)
    );
    return maximum;    
}