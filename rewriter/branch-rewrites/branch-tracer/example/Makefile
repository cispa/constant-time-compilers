all: example-x86 example-aarch64 example-riscv64

example-x86: example.c
	gcc example.c -o example-x86 -static

example-aarch64: example.c
	aarch64-linux-gnu-gcc example.c -o example-aarch64 -static

example-riscv64: example.c
	riscv64-linux-gnu-gcc example.c -o example-riscv64 -static

clean: 
	rm example-x86 example-aarch64 example-riscv64