# Multiarch branch recorder framework
Allows to produce branch traces on multipe architectures. Currently supported:
- x86_64  (amd64)
- aarch64 (arm64)
- riscv-64

# Setup
Install requirements using
```
pip3 install -r requirements.txt
```

# Usage 
```
Usage: branch-tracer.py [OPTIONS] PROGRAM [ARGS] LOGFILE

  Produce branch trace of a program. Arguments can be provided whith the ARGS
  parameter. The results of the trace are written to LOGFILE.

Options:
  --function TEXT                 Function to trace
  --rootfs TEXT                   Rootfs for binary
  --verbose [OFF|DEFAULT|DEBUG|DISASM]
  --help                          Show this message and exit.
```

# Limitations
- Some instuctions are skipped but the can be manually emulated

