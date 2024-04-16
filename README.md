# CTCCP - A constant-time compiler checking pipeline

CTCCP allows to automatically check how different C compilers and optimization levels change the behavior of constant-time code.

## Building the framework
This framework depends on a lot of other projects and does not run in Docker containers due to restrictions by some used checkers.
Instead, it is intended to be run in a Ubuntu 22.04 VM, for which there is an automatic installation script provided. 
Do not install CTCCP on your host system unless you plan to reinstall it afterwards!

You can install all required tools and libraries by calling `install.sh`.