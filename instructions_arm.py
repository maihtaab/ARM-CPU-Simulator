from flags import set_flags

def decode_and_execute_arm(cpu, instr, cur_pc):
    r, m, f = cpu.registers, cpu.memory, cpu.flags

    if (instr & 0x0FFFFFF0) == 0x012FFF10:  # BX
        Rm     = instr & 0xF
        target = r[Rm]
        cpu.thumb_mode = bool(target & 1)
        cpu.pc        = target & ~1
        print(f"    → BX   R{Rm} → 0x{cpu.pc:08X}  Z={f['Z']} N={f['N']} C={f['C']} V={f['V']}")
        cpu.print_registers()
        return

    if ((instr >> 26) & 0x3) == 0 and ((instr >> 25) & 1) == 1:  # Data processing
        opcode = (instr >> 21) & 0xF
        Rn, Rd = (instr >> 16) & 0xF, (instr >> 12) & 0xF
        imm    = instr & 0xFF

        # signed‐conversion for overflow test
        def signed(val):
            return val if val < 0x80000000 else val - 0x100000000

        if opcode == 0xD:  # MOV
            res   = imm
            r[Rd] = res
            set_flags(f, res)  # updates Z & N only
            print(f"    → MOV  R{Rd}, #{imm}  Z={f['Z']} N={f['N']} C={f['C']} V={f['V']}")

        elif opcode == 0x4:  # ADD
            A      = r[Rn]
            full   = A + imm
            res    = full & 0xFFFFFFFF
            r[Rd]  = res
            carry  = full > 0xFFFFFFFF
            sA     = signed(A)
            sI     = signed(imm)
            sR     = signed(res)
            overflow = (sA >= 0 and sI >= 0 and sR < 0) or (sA < 0 and sI < 0 and sR >= 0)
            set_flags(f, res, carry, overflow)
            print(f"    → ADD  R{Rd}, R{Rn}, #{imm}  Z={f['Z']} N={f['N']} C={f['C']} V={f['V']}")

        elif opcode == 0x2:  # SUB
            A      = r[Rn]
            full   = A - imm
            res    = full & 0xFFFFFFFF
            r[Rd]  = res
            borrow = A < imm
            sA     = signed(A)
            sI     = signed(imm)
            sR     = signed(res)
            overflow = (sA >= 0 and sI < 0 and sR < 0) or (sA < 0 and sI >= 0 and sR >= 0)
            set_flags(f, res, not borrow, overflow)  # C = 1 if no borrow
            print(f"    → SUB  R{Rd}, R{Rn}, #{imm}  Z={f['Z']} N={f['N']} C={f['C']} V={f['V']}")

        elif opcode == 0xA:  # CMP
            A      = r[Rn]
            full   = A - imm
            res    = full & 0xFFFFFFFF
            borrow = A < imm
            sA     = signed(A)
            sI     = signed(imm)
            sR     = signed(res)
            overflow = (sA >= 0 and sI < 0 and sR < 0) or (sA < 0 and sI >= 0 and sR >= 0)
            set_flags(f, res, not borrow, overflow)
            print(f"    → CMP  R{Rn}, #{imm}  Z={f['Z']} N={f['N']} C={f['C']} V={f['V']}")

        elif opcode == 0x0:  # AND
            res    = r[Rn] & imm
            r[Rd]  = res
            set_flags(f, res)  # Z & N only
            print(f"    → AND  R{Rd}, R{Rn}, #{imm}  Z={f['Z']} N={f['N']} C={f['C']} V={f['V']}")

        elif opcode == 0xC:  # ORR
            res    = r[Rn] | imm
            r[Rd]  = res
            set_flags(f, res)
            print(f"    → ORR  R{Rd}, R{Rn}, #{imm}  Z={f['Z']} N={f['N']} C={f['C']} V={f['V']}")

        else:
            print("ERROR: ARM opcode not supported  "
                  f"Z={f['Z']} N={f['N']} C={f['C']} V={f['V']}")
        cpu.print_registers()
        return

    if ((instr >> 26) & 0x3) == 1:  # LDR / STR
        U, L   = (instr >> 23) & 1, (instr >> 20) & 1
        Rn, Rd = (instr >> 16) & 0xF, (instr >> 12) & 0xF
        offset = instr & 0xFFF
        addr   = (r[Rn] + (offset if U else -offset)) & 0xFFFFFFFF

        if L:  # LDR through data cache 
            val = 0 
            for i in range(4): 
                byte = cpu.cache.read_byte(addr + i) 
                val |= (byte << (8 * i)) 
            r[Rd] = val 
            print(f"    → LDR  R{Rd}, [R{Rn}, #{offset}]  Z={f['Z']} N={f['N']} C={f['C']} V={f['V']}") 
        else:  # STR through data cache 
            word = r[Rd] 
            for i in range(4): 
                byte = (word >> (8 * i)) & 0xFF 
                cpu.cache.write_byte(addr + i, byte) 
            print(f"    → STR  R{Rd}, [R{Rn}, #{offset}]  Z={f['Z']} N={f['N']} C={f['C']} V={f['V']}")
        cpu.print_registers()
        return

    cond = (instr >> 28) & 0xF # B (only unconditional AL cond=1110)
    if cond == 0xE and ((instr >> 25) & 0x7) == 5:
        imm24 = instr & 0xFFFFFF
        if imm24 & 0x800000:  # sign extend
            imm24 |= ~0xFFFFFF
        offset    = (imm24 << 2) & 0xFFFFFFFF
        cpu.pc    = (cur_pc + offset) & 0xFFFFFFFF
        print(f"    → B    to 0x{cpu.pc:08X}  Z={f['Z']} N={f['N']} C={f['C']} V={f['V']}")
        cpu.print_registers()
        return

    print("ERROR: ARM instruction not implemented  "
          f"Z={f['Z']} N={f['N']} C={f['C']} V={f['V']}")