# Branch tracer 
This tracer benchmarks code and detecs which branches are taken. 
Currently works on x86, Arm and RISCV.

# Debrancher
All branches that are never taken are statically patched out from the binary.
This is simmilar to dynamic dead code removal and can increase the accuracy of dynamic analysis on the binary.

# Speculative execution emulation
Versions of the binary where branches that are never taken get inverted are created. 
This emulates the behaviour of the binary under speculative execution and can be used to test the constant time properties of the binary with regards to speculative execution.
