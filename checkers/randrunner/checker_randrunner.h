#define RANDRUNNER_IMPLEMENTATION
#include <stdint.h>
#include "randrunner.h"
#include "checker_random.h"
#include "time.h"

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

int main() {
    srand(time(NULL));
    for (int dudect_runs = 0; dudect_runs < 10; dudect_runs++) {
        dudect_config_t config = {
            .chunk_size = sizeof(checker_dudect_args_t),
            .number_measurements = 1e5 * 5,
        };
        dudect_ctx_t context;
        checker_dudect_fill_template();
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