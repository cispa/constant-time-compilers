#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>
#include <stdint.h>

#ifndef CHECKER_RANDOM_H
#define CHECKER_RANDOM_H 1

#define CHECKER_RANDOMNESS_BUFFER 4096

char checker_randomness[CHECKER_RANDOMNESS_BUFFER];
size_t checker_randomness_offset = CHECKER_RANDOMNESS_BUFFER;

/**
 * Refills the buffer of random data
 */
static void checker_random_refill()
{
  #ifdef CHECKER_RANDOM_DEVURANDOM
  static int fd = -1;
  if (fd == -1) {
    while (1) {
      fd = open("/dev/urandom", O_RDONLY);
      if (fd != -1)
        break;
      sleep(1);
    }
  }
  read(fd, &checker_randomness, sizeof(checker_randomness));
  #else
  for (size_t offset = 0; offset < CHECKER_RANDOMNESS_BUFFER; offset++) {
    checker_randomness[offset] = (char) rand();
  }
  #endif
  checker_randomness_offset = 0;
}

/**
 * Returns a pointer to amount many bytes of random data
 */
void *checker_random_data(size_t amount)
{
  if (amount > sizeof(checker_randomness))
  {
    return NULL;
  }
  if (checker_randomness_offset + amount > sizeof(checker_randomness))
  {
    checker_random_refill();
  }
  char *data = checker_randomness + checker_randomness_offset;
  checker_randomness_offset += amount;
  return data;
}

/**
 * Fills target with elements many blocks of size element_size bytes of random data
 */
//#include <stdio.h>
void checker_fill_unconstrained(void *target, size_t elements, size_t element_size)
{
  for (size_t element = 0; element < elements; element++)
  {
    void *randomness = checker_random_data(element_size);
    //printf("random: %p\ntarget: %p\n", randomness, target);
    memcpy(target, randomness, element_size);
  }
}

/**
 * Fills target with elements many blocks of the fixed value
 */
void checker_fill_fixed(void *target, unsigned long fixed_value, size_t elements, size_t element_size)
{
  for (size_t element = 0; element < elements; element++)
  {
    memcpy(target, &fixed_value, element_size);
  }
}

/**
 * Fills target with random values within the given range
 * This only works on little-endian machines!
 */
void checker_fill_range(void *target, unsigned long range_start, unsigned long range_end, size_t elements, size_t element_size)
{
  for (size_t element = 0; element < elements; element++)
  {
    unsigned long *randomness = (unsigned long *)checker_random_data(element_size);
    *randomness = range_start + (*randomness % (range_end - range_start + 1));
    memcpy(target, randomness, element_size);
  }
}

/**
 * Limits all elements of data to the range [lower, upper].
 */
void checker_limit_to_bounds_8(uint8_t *data, size_t elements, size_t lower, size_t upper)
{
  for (size_t i = 0; i < elements; i++)
  {
    volatile size_t element = data[i];
    asm volatile(
        "mov %1, %0\n\t"
        "cmp %2, %0\n\t"
        "cmova %2, %0\n\t"
        "cmp %3, %0\n\t"
        "cmovb %3, %0\n\t"
        : "=r"(element)
        : "r"(element), "r"(upper), "r"(lower));
    data[i] = (uint8_t)element;
  }
}


/**
 * Limits all elements of data to the range [lower, upper].
 */
void checker_limit_to_bounds_16(uint16_t *data, size_t elements, size_t lower, size_t upper)
{
  for (size_t i = 0; i < elements; i++)
  {
    volatile size_t element = data[i];
    asm volatile(
        "mov %1, %0\n\t"
        "cmp %2, %0\n\t"
        "cmova %2, %0\n\t"
        "cmp %3, %0\n\t"
        "cmovb %3, %0\n\t"
        : "=r"(element)
        : "r"(element), "r"(upper), "r"(lower));
    data[i] = (uint16_t)element;
  }
}


/**
 * Limits all elements of data to the range [lower, upper].
 */
void checker_limit_to_bounds_32(uint32_t *data, size_t elements, size_t lower, size_t upper)
{
  for (size_t i = 0; i < elements; i++)
  {
    volatile size_t element = data[i];
    asm volatile(
        "mov %1, %0\n\t"
        "cmp %2, %0\n\t"
        "cmova %2, %0\n\t"
        "cmp %3, %0\n\t"
        "cmovb %3, %0\n\t"
        : "=r"(element)
        : "r"(element), "r"(upper), "r"(lower));
    data[i] = (uint32_t)element;
  }
}


/**
 * Limits all elements of data to the range [lower, upper].
 */
void checker_limit_to_bounds_64(uint64_t *data, size_t elements, size_t lower, size_t upper)
{
  for (size_t i = 0; i < elements; i++)
  {
    volatile size_t element = data[i];
    asm volatile(
        "mov %1, %0\n\t"
        "cmp %2, %0\n\t"
        "cmova %2, %0\n\t"
        "cmp %3, %0\n\t"
        "cmovb %3, %0\n\t"
        : "=r"(element)
        : "r"(element), "r"(upper), "r"(lower));
    data[i] = (uint64_t)element;
  }
}
#endif