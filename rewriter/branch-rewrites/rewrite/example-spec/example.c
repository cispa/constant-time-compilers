#include <valgrind/memcheck.h>
#include <stdlib.h>
#include <stdio.h>

int lookup[1000] = {0};

int main(int argc, char** argv) {
  unsigned volatile int key = atoi(argv[1]);
  VALGRIND_MAKE_MEM_UNDEFINED(&key, sizeof(int));

  // This branch is never taken
  if(argc != 2){
    printf("spec\n");
    lookup[key] = key;
  }

}