class Memory:
    def __init__(self, size):
        self.mem = bytearray(size)

    def load_binary(self, filename):
        with open(filename, "rb") as f:
            data = f.read()
        self.mem[:len(data)] = data
        return data

    def fetch_word(self, addr):
        return int.from_bytes(self.mem[addr:addr+4], "little")

    def fetch_halfword(self, addr):
        return int.from_bytes(self.mem[addr:addr+2], "little")

    def read_word(self, addr):
        return self.fetch_word(addr)

    def write_word(self, addr, value):
        self.mem[addr:addr+4] = value.to_bytes(4, "little")
        print(f"    ↪ MEMORY WRITE: [0x{addr:08X}] ← 0x{value:08X}")
        
    def read_byte(self, addr): 
        # return zero for out‑of‑bounds reads 
        if addr < 0 or addr >= len(self.mem): 
            return 0 
        return self.mem[addr]
 
    def write_byte(self, addr, val): 
        # ignore out‑of‑bounds writes 
        if addr < 0 or addr >= len(self.mem): 
            return 
        self.mem[addr] = val