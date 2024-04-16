extern crate crabgrind;
use aria::Aria128;
use std::ffi::c_void;

use aria::cipher::generic_array::GenericArray;
use aria::cipher::{BlockEncrypt, BlockDecrypt, KeyInit};

use belt_block::{
    cipher::{BlockCipherDecrypt, BlockCipherEncrypt, KeyInit},
    BeltBlock,
};

fn main() {
    test_aria();
    test_belt();
}


fn test_aria(){
    let k: [u8; 16] = [0u8; 16];
    let _ = crabgrind::memcheck::mark_mem( k.as_ref().as_ptr() as *mut c_void, k.len(), crabgrind::memcheck::MemState::Undefined);
    let key = GenericArray::from(k);
    let mut block = GenericArray::from([0u8; 16]);    
    // Initialize cipher
    let cipher = Aria128::new(&key);
    // Encrypt block in-place
    cipher.encrypt_block(&mut block);
    // And decrypt it back
    cipher.decrypt_block(&mut block);
}

fn test_belt(){
    let k: [u8; 8] = [0u8; 8];
    let _ = crabgrind::memcheck::mark_mem( k.as_ref().as_ptr() as *mut c_void, k.len(), crabgrind::memcheck::MemState::Undefined);
    let key = GenericArray::from(k);
    let mut block = GenericArray::from([0u8; 4]);    
    let mut pt = GenericArray::from([0u8; 4]);    
    // Initialize cipher
    let cipher = BeltBlock::new(&key.into());
    let mut block = pt.into();
    cipher.encrypt_block(&mut block);
}

fn test_blowfish(){

}

fn test_camellia(){

}

fn test_cast5(){

}

fn test_cast6(){

}

fn test_des(){

}

fn test_idea(){

}

fn test_kuznyechik(){

}

fn test_magma(){

}

fn test_rc2(){

}

fn test_rc5(){

}


