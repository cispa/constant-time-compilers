import sys
import lief

conditional = [
 ("N/A", [0x00], "N/A"),
 ("jo", [0x70], "jno"),
 ("jno", [0x71], "jo"),
 ("jb", [0x72], "jae"),
 ("jae", [0x73], "jb"),
 ("je", [0x74], "jne"),
 ("jne", [0x75], "je"),
 ("jbe", [0x76], "ja"),
 ("ja", [0x77], "jbe"),
 ("js", [0x78], "jns"),
 ("jns", [0x79], "js"),
 ("jp", [0x7a], "jnp"),
 ("jnp", [0x7b], "jp"),
 ("jl", [0x7c], "jge"),
 ("jge", [0x7d], "jl"),
 ("jle", [0x7e], "jg"),
 ("jg", [0x7f], "jle"),
 ("jcxz", [0xE3], "N/A"),
 ("jecxz", [0xE3], "N/A"),

 ("jo_l", [0x0F, 0x80], "jno_l"),
 ("jno_l", [0x0F, 0x81], "jo_l"),
 ("jb_l", [0x0F, 0x82], "jae_l"),
 ("jae_l", [0x0F, 0x83], "jb_l"),
 ("je_l", [0x0F, 0x84], "jne_l"),
 ("jne_l", [0x0F, 0x85], "je_l"),
 ("jbe_l", [0x0F, 0x86], "ja_l"),
 ("ja_l", [0x0F, 0x87], "jbe_l"),
 ("js_l", [0x0F, 0x88], "jns_l"),
 ("jns_l", [0x0F, 0x89], "js_l"),
 ("jp_l", [0x0F, 0x8A], "jnp_l"),
 ("jnp_l", [0x0F, 0x8B], "jp_l"),
 ("jl_l", [0x0F, 0x8C], "jge_l"),
 ("jge_l", [0x0F, 0x8D], "jl_l"),
 ("jle_l", [0x0F, 0x8E], "jg_l"),
 ("jg_l", [0x0F, 0x8F], "jle_l")
]

unconditional = [
 ("jmp", [0xEB], "N/A"),
 ("jmp_l", [0xE9], "N/A")
]

def patch(fn, out, invert = [], always = [], never = []):
    #md = Cs(CS_ARCH_X86, CS_MODE_64)
    binary = lief.parse(fn)
    text = binary.get_section(".text")
    base = text.virtual_address
    print("%x (%x)" % (base, text.file_offset))

    orig = bytearray(open(fn, "rb").read())
    code = orig[text.file_offset:] #text.content
    log = open(log).read().strip().split("\n")
    invert = [addr-base for addr in invert]
    always = [addr-base for addr in always]
    never =  [addr-base for addr in never]
    branch_offsets = invert+always+never
    
    for b in branch_offsets:
        print("@0x%x <+0x%x>: %02x %02x %02x" % (b + base, b, code[b], code[b + 1], code[b + 2]))
        
        # disassemble
        jmp = conditional[0]
        for con in conditional:
            mem = [int(x) for x in code[b:b+len(con[1])]]
            if mem == con[1]:
                jmp = con
                break
        # invert conditional branch
        if b in invert:
            if jmp[0] != "N/A":
                # find opposite
                patch_jmp = None
                for con in conditional:
                    if con[0] == jmp[2]:
                        patch_jmp = con
                        break
            if not patch_jmp:
                print("Could not patch %s" % jmp[0])
            else:
                print("Patching %s to %s" % (jmp[0], patch_jmp[0]))
                for i in range(len(jmp[1])):
                    orig[text.file_offset+b+i] = patch_jmp[1][i]
                
        # convert to always taken
        if b in always:
            if "_l" in jmp[0]:
                orig[text.file_offset+b] = 0xE9
            else:
                orig[text.file_offset+b] = 0xEB
        
        # convert to never taken
        if b in never:
            if "_l" in jmp[0]:
                for i in range(6): 
                    orig[text.file_offset+b+i] = 0x90
            else:
                for i in range(2): 
                    orig[text.file_offset+b+i] = 0x90
        
        #for i in md.disasm(code[b:b+15], 0):
            #print("%s" % i.mnemonic)
            #break
    
    # save new file
    o = open(out, "wb")
    o.write(orig)
    o.close()

    

if __name__ == "__main__":
    patch(sys.argv[1], sys.argv[2], sys.argv[3], never = [60])
