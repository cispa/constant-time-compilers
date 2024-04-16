dudect++: extended dudect implementation
=======================================

## Added features
- Support for ARM and RISC-V
- Support for performance counter based benchmarking 

## Building
### X86
   ```make  -Dx86_64```
### ARM
   ```make  -D__aarch64__```
### RISCV
   ```make  -D__riscv```
### Performance counters
   Pick a performance counter which you want to use for benchmarking from `perf_event.h`
   then do.

   ```make CFLAGS="-DPERFCNT -DPERF_COUNT_SELECT=<your-counter>"```