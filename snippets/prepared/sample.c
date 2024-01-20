#include <stdlib.h>
#include <stdlib.h>

typedef struct {
    int x;
    int y;
} input_data;

void test_prepared(input_data* data) {
    if (data->x == 5) {
        data->y++;
    } else {
        data->y--;
        data->x--;
    }
}

void test_unprepared(int x, int y) {
    input_data data = {
        x,
        y
    };
    test_prepared(&data);
}

void prepare_input(input_data* data) {
    data->x = 5;
    data->y = rand();
}