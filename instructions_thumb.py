from flags import set_flags

def decode_and_execute_thumb(cpu, instr, cur_pc):
    r, f = cpu.registers, cpu.flags

    if (instr & 0xF800) == 0x2000:  # MOV
        Rd   = (instr >> 8) & 0x7
        imm  = instr & 0xFF
        res  = imm
        r[Rd] = res
        set_flags(f, res)   # Z & N only
        print(f"    → MOV  R{Rd}, #{imm}  Z={f['Z']} N={f['N']} C={f['C']} V={f['V']}")
        cpu.print_registers()

    elif (instr & 0xF800) == 0x3000:  # ADD
        Rd    = (instr >> 8) & 0x7
        imm   = instr & 0xFF
        A     = r[Rd]
        full  = A + imm
        res   = full & 0xFFFFFFFF
        r[Rd] = res
        carry = full > 0xFFFFFFFF
        # overflow if A and imm have same sign but res differs
        overflow = bool((A ^ res) & (imm ^ res) & 0x80000000)
        set_flags(f, res, carry, overflow)
        print(f"    → ADD  R{Rd}, #{imm}  Z={f['Z']} N={f['N']} C={f['C']} V={f['V']}")
        cpu.print_registers()

    elif (instr & 0xF800) == 0x3800:  # SUB
        Rd    = (instr >> 8) & 0x7
        imm   = instr & 0xFF
        A     = r[Rd]
        full  = A - imm
        res   = full & 0xFFFFFFFF
        r[Rd] = res
        borrow = A < imm
        # overflow if A and imm differ in sign and res sign differs from A
        overflow = bool((A ^ imm) & (A ^ res) & 0x80000000)
        set_flags(f, res, not borrow, overflow)  # C=1 if no borrow
        print(f"    → SUB  R{Rd}, #{imm}  Z={f['Z']} N={f['N']} C={f['C']} V={f['V']}")
        cpu.print_registers()

    elif (instr & 0xF800) == 0xE000:  # B
        imm11 = instr & 0x7FF
        if imm11 & 0x400:
            imm11 |= ~0x7FF
        offset = (imm11 << 1) & 0xFFFFFFFF
        cpu.pc = (cur_pc + offset) & 0xFFFFFFFF
        # flags unchanged
        print(f"    → B    to 0x{cpu.pc:08X}  Z={f['Z']} N={f['N']} C={f['C']} V={f['V']}")
        cpu.print_registers()

    elif instr == 0x46C0:  # NOP
        print(f"    → NOP  Z={f['Z']} N={f['N']} C={f['C']} V={f['V']}")
        cpu.print_registers()

    else:
        print(f"ERROR: THUMB instruction not implemented  Z={f['Z']} N={f['N']} C={f['C']} V={f['V']}")
