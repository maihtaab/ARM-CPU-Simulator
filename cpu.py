from memory import Memory
from instructions_arm import decode_and_execute_arm
from instructions_thumb import decode_and_execute_thumb
from cache import CacheHierarchy 
import config

class CPU:
    def __init__(self):
        self.registers = [0] * 16  # R0–R15 (R15 is the PC)
        self.memory = Memory(1024 * 1024)  # 1MB of RAM
        self.pc = 0                # Program counter
        self.thumb_mode = False    # Starts in ARM mode
        self.flags     = {"Z": 0, "N": 0, "C": 0, "V": 0}  # All flags
        self.running = True        # Stop condition

        self.cache = CacheHierarchy( 
            config.L1_TYPE, 
            config.L1_SIZE, 
            config.L1_BLOCK_SIZE, 
            config.L2_TYPE, 
            config.L2_SIZE, 
            config.L2_BLOCK_SIZE, 
            self.memory 
        )
        
    def load_binary(self, filename):
        # Load binary file into memory starting at address 0
        binary = self.memory.load_binary(filename)
        self.binary_length = len(binary)

    def run(self):
        # Instruction loop
        instruction_count = 1  # Start at instruction 1
        while self.running and self.pc < self.binary_length:
            cur_pc = self.pc
            print(f"\nInstruction {instruction_count}")  # Print instruction number
            instruction_count += 1

            if not self.thumb_mode:
                # instr = self.memory.fetch_word(self.pc)
                instr = self.cache.fetch_word(self.pc)
                print(f"PC={cur_pc:08X} [ARM]  Instr={instr:08X}")
                self.pc += 4
                decode_and_execute_arm(self, instr, cur_pc)
            else:
                # instr = self.memory.fetch_halfword(self.pc)
                instr = self.cache.fetch_halfword(self.pc)
                print(f"PC={cur_pc:08X} [THUMB]Instr={instr:04X}")
                self.pc += 2
                decode_and_execute_thumb(self, instr, cur_pc)

    def print_registers(self):
        print("    ↪ REGISTERS:")
        for i in range(0, 16, 4):
            print("    ", end="")
            for j in range(4):
                reg_num = i + j
                print(f"R{reg_num:<2} = {self.registers[reg_num]:08X}  ", end="")
            print()
        print()


