#define DUDECT_IMPLEMENTATION
#include <stdint.h>
#include "dudect.h"
#include "checker_random.h"
#include "time.h"

#ifdef DUDECT_PREPARATION_FUNCTION
void prepare_inputs(dudect_config_t *config, uint8_t *raw_data, uint8_t *classes) {
    void* fixed = malloc(DUDECT_PREPARATION_SIZE);
    DUDECT_PREPARATION_FUNCTION(fixed);
    for (size_t i = 0; i < config->number_measurements; i++) {
        classes[i] = randombit();
        if (classes[i]) {
            memcpy(raw_data + (i * DUDECT_PREPARATION_SIZE), fixed, DUDECT_PREPARATION_SIZE);
        } else {
            DUDECT_PREPARATION_FUNCTION(raw_data + (i * DUDECT_PREPARATION_SIZE));
        }
    }
    free(fixed);
}

#else
void checker_dudect_fill_struct(checker_dudect_args_t*, checker_dudect_args_t*);
void checker_dudect_fill_template();

void prepare_inputs(dudect_config_t *config, uint8_t *raw_data, uint8_t *classes) {
    checker_dudect_args_t fixed;
    checker_dudect_fill_struct(&fixed, NULL);
    checker_dudect_args_t *data = (void*) raw_data;
    for (size_t i = 0; i < config->number_measurements; i++) {
        classes[i] = randombit();
        checker_dudect_fill_struct(data + i, classes[i] ? (&fixed) : NULL);
    }
}
#endif

int main() {
    srand(time(NULL));
    for (int dudect_runs = 0; dudect_runs < 10; dudect_runs++) {
        dudect_config_t config = {
#ifdef DUDECT_PREPARATION_SIZE
            .chunk_size = DUDECT_PREPARATION_SIZE,
#else
            .chunk_size = sizeof(checker_dudect_args_t),
#endif
            .number_measurements = 1e5 * 5,
        };
        dudect_ctx_t context;
#ifndef DUDECT_PREPARATION_SIZE
        checker_dudect_fill_template();
#endif
        dudect_init(&context, &config);
        for (int run_invocation = 0; run_invocation < 3; run_invocation++) {
            dudect_state_t result = dudect_main(&context);
            if (result == DUDECT_LEAKAGE_SURE) {
                dudect_free(&context);
                return 1;
            }
            if (run_invocation > 0 && result == DUDECT_NO_LEAKAGE_EVIDENCE_YET) {
                break;
            }
        }
        dudect_free(&context);
    }
    return 0;
}