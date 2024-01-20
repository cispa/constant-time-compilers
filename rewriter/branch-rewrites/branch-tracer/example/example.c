#include <stdio.h>
#include <stdlib.h>

int main(int argc, char** argv){
    int cond = atoi(argv[1]);
    if(cond >= 0){
        printf("a");
    }
    if(cond >= 1){
        printf("b");
    }
    if(cond >= 2){
        printf("c");
    }
    if(cond >= 3){
        printf("d");
    }
}