#include "cttk.h"

void test_oram(void* arr1, void* arr2, size_t len, uint32_t ctl_in){
    cttk_bool ctl = cttk_bool_of_s32(ctl_in);
    cttk_cond_swap(ctl, arr1, arr2, len/2);
    cttk_array_cmp(arr1,arr2,len);
    cttk_array_eq(arr1,arr2,len);
    cttk_array_neq(arr1,arr2,len);
}