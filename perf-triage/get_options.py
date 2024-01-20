import subprocess
import os 
from shlex import split

def get_flags(opt_level):
    res = subprocess.check_output(f"llvm-as < /dev/null | opt -{opt_level} -disable-output -debug-pass=Arguments -enable-new-pm=0",stderr=subprocess.STDOUT, shell=True)
    flags = split(res.decode().strip().replace("Pass Arguments:","").replace("\n",""))
    return set(flags) 

def get_option_change(set1,set2):
    added = set()
    removed = set()
    for elem in set1:
        if elem not in set2:
            removed.add(elem)
    for elem in set2:
        if elem not in set1:
            added.add(elem)
    return added, removed

flag_lst = [get_flags(opt_level) for opt_level in ["O0","O1","O2","O3","Os"]]

# Get common flags
intersect = flag_lst[0].intersection(*flag_lst)

# Remove common flags
for e in flag_lst:
    e = e.difference(intersect)

# Get changes in compiler flags
changes = []
for i in range(0,4):
    changes.append(get_option_change(flag_lst[i],flag_lst[i+1]))    

print(changes)