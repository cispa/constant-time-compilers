use dudect_bencher::{ctbench_main, BenchRng, Class, CtRunner};
use rand::{Rng, RngCore};

// Return a random vector of length len
fn rand_vec(len: usize, rng: &mut BenchRng) -> Vec<u8> {
    let mut arr = vec![0u8; len];
    rng.fill(arr.as_mut_slice());
    arr
}

fn unsafe_compare(expected: Vec<u8>, actual : Vec<u8>, len: usize) -> bool{
    let mut idx = 0;
    while idx < len {
        if expected[idx] != actual[idx]{
            return false;  
        } 
        idx += 1;
    }
    return true;
}

fn safe_compare(expected: Vec<u8>, actual : Vec<u8>, len: usize) -> bool{
    let mut idx = 0;
    let mut result = true;
    while idx < len {
        result &= expected[idx] == actual[idx];
        idx += 1;
    }
    return result;
}

// Benchmark for equality of vectors. This does an early return when it finds an
// inequality, so it should be very much not constant-time
fn compare_bench_safe(runner: &mut CtRunner, rng: &mut BenchRng) {
    // Make vectors of size 100
    let vlen = 100;
    let mut inputs: Vec<(Vec<u8>, Vec<u8>)> = Vec::new();
    let mut classes = Vec::new();

    // Make 100,000 random pairs of vectors
    for _ in 0..100_000 {
        // Flip a coin. If true, make a pair of vectors that are equal to each
        // other and put it in the Left distribution
        if rng.gen::<bool>() {
            let v1 = rand_vec(vlen, rng);
            let v2 = v1.clone();
            inputs.push((v1, v2));
            classes.push(Class::Left);
        }
        // Otherwise, make a pair of random vectors and put them in the Right distribution
        else {
            let v1 = rand_vec(vlen, rng);
            let v2 = rand_vec(vlen, rng);
            inputs.push((v1, v2));
            classes.push(Class::Right);
        }
    }

    for (class, (u, v)) in classes.into_iter().zip(inputs.into_iter()) {
        // Now time how long it takes to do a vector comparison
        runner.run_one(class, || safe_compare(u.clone(),v.clone(),vlen));
    }
}

// Benchmark for equality of vectors. This does an early return when it finds an
// inequality, so it should be very much not constant-time
fn compare_bench_unsafe(runner: &mut CtRunner, rng: &mut BenchRng) {
    // Make vectors of size 100
    let vlen = 100;
    let mut inputs: Vec<(Vec<u8>, Vec<u8>)> = Vec::new();
    let mut classes = Vec::new();

    // Make 100,000 random pairs of vectors
    for _ in 0..100_000 {
        // Flip a coin. If true, make a pair of vectors that are equal to each
        // other and put it in the Left distribution
        if rng.gen::<bool>() {
            let v1 = rand_vec(vlen, rng);
            let v2 = v1.clone();
            inputs.push((v1, v2));
            classes.push(Class::Left);
        }
        // Otherwise, make a pair of random vectors and put them in the Right distribution
        else {
            let v1 = rand_vec(vlen, rng);
            let v2 = rand_vec(vlen, rng);
            inputs.push((v1, v2));
            classes.push(Class::Right);
        }
    }

    for (class, (u, v)) in classes.into_iter().zip(inputs.into_iter()) {
        // Now time how long it takes to do a vector comparison
        runner.run_one(class, || unsafe_compare(u.clone(),v.clone(),vlen));
    }
}
// Crate the main function to include the bench for vec_eq
ctbench_main!(compare_bench_unsafe,compare_bench_safe);
