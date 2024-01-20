#include "../../bearssl/bearssl-git/inc/bearssl.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

/**
 * KEY: 256 bits = 32 bytes
 * IV: 128 bits = 16 bytes
 * PLAIN: 32 bytes
*/
static void run_aes_cbc_encryption(void* key, void* iv, void* plain, br_block_cbcenc_class* ve) {
	br_aes_gen_cbcenc_keys v_ec = {0};
	const br_block_cbcenc_class **ec = &v_ec.vtable;
    unsigned char buf[64];
    memcpy(buf, plain, 32);
    ve->init(ec, key, 32);
    ve->run(ec, iv, buf, 32);
}

/**
 * KEY: 256 bits = 32 bytes
 * IV: 128 bits = 16 bytes
 * PLAIN: 32 bytes
*/
void test_aes_big_cbc(unsigned char* key, unsigned char* iv, unsigned char* plain) {
    run_aes_cbc_encryption(key, iv, plain, &br_aes_big_cbcenc_vtable);
}

/**
 * KEY: 256 bits = 32 bytes
 * IV: 128 bits = 16 bytes
 * PLAIN: 32 bytes
*/
void test_aes_small_cbc(unsigned char* key, unsigned char* iv, unsigned char* plain) {
    run_aes_cbc_encryption(key, iv, plain, &br_aes_small_cbcenc_vtable);
}


/**
 * KEY: 256 bits = 32 bytes
 * IV: 128 bits = 16 bytes
 * PLAIN: 32 bytes
*/
void test_aes_ct_cbc(unsigned char* key, unsigned char* iv, unsigned char* plain) {
    run_aes_cbc_encryption(key, iv, plain, &br_aes_ct_cbcenc_vtable);
}


/**
 * KEY: 256 bits = 32 bytes
 * IV: 128 bits = 16 bytes
 * PLAIN: 32 bytes
*/
void test_aes_ct64_cbc(unsigned char* key, unsigned char* iv, unsigned char* plain) {
    run_aes_cbc_encryption(key, iv, plain, &br_aes_ct64_cbcenc_vtable);
}

/**
 * KEY: 256 bits = 32 bytes
 * IV: 128 bits = 16 bytes
 * PLAIN: 32 bytes
*/
static void run_aes_ctr_encryption(void* key, void* iv, void* plain, br_block_ctr_class* vc) {
	br_aes_gen_ctr_keys v_xc = {0};
	const br_block_ctr_class **xc = &v_xc.vtable;
    unsigned char buf[64];
    memcpy(buf, plain, 32);
    vc->init(xc, key, 32);
    vc->run(xc, iv, 0xDEAD, buf, 32);
}

/**
 * KEY: 256 bits = 32 bytes
 * IV: 128 bits = 16 bytes
 * PLAIN: 32 bytes
*/
void test_aes_big_ctr(unsigned char* key, unsigned char* iv, unsigned char* plain) {
    run_aes_ctr_encryption(key, iv, plain, &br_aes_big_ctr_vtable);
}

/**
 * KEY: 256 bits = 32 bytes
 * IV: 128 bits = 16 bytes
 * PLAIN: 32 bytes
*/
void test_aes_small_ctr(unsigned char* key, unsigned char* iv, unsigned char* plain) {
    run_aes_ctr_encryption(key, iv, plain, &br_aes_small_ctr_vtable);
}

/**
 * KEY: 256 bits = 32 bytes
 * IV: 128 bits = 16 bytes
 * PLAIN: 32 bytes
*/
void test_aes_ct_ctr(unsigned char* key, unsigned char* iv, unsigned char* plain) {
    run_aes_ctr_encryption(key, iv, plain, &br_aes_ct_ctr_vtable);
}


/**
 * KEY: 256 bits = 32 bytes
 * IV: 128 bits = 16 bytes
 * PLAIN: 32 bytes
*/
void test_aes_ct64_ctr(unsigned char* key, unsigned char* iv, unsigned char* plain) {
    run_aes_ctr_encryption(key, iv, plain, &br_aes_ct64_ctr_vtable);
}