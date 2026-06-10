from memory import Memory

class CacheLevel:
    def __init__(self, size, block_size, assoc, next_level):
        self.size        = size
        self.block_size  = block_size
        self.assoc       = assoc
        self.next        = next_level
        # number of sets = (total blocks) / associativity
        self.num_sets    = (size // block_size) // assoc

        # build empty sets
        self.sets = []
        for _ in range(self.num_sets):
            one_set = []
            for _ in range(assoc):
                line = {
                    'tag': None,
                    'valid': False,
                    'dirty': False,
                    'data': bytearray(block_size)
                }
                one_set.append(line)
            self.sets.append(one_set)

        # counters for hit/miss/writeback
        self.hits       = 0
        self.misses     = 0
        self.writebacks = 0

    def _loc(self, addr):
        block      = addr // self.block_size
        set_idx    = block % self.num_sets
        tag        = block // self.num_sets
        offset     = addr % self.block_size
        block_base = block * self.block_size
        return set_idx, tag, offset, block_base

    def read_byte(self, addr):
        set_idx, tag, offset, base = self._loc(addr)

        # hit
        for line in self.sets[set_idx]:
            if line['valid'] and line['tag'] == tag:
                self.hits += 1
                return line['data'][offset]

        # miss: remove the first line
        self.misses += 1
        victim = self.sets[set_idx][0]

        # write back if dirty
        if victim['valid'] and victim['dirty']:
            self.writebacks += 1
            wb_block = (victim['tag'] * self.num_sets + set_idx)
            wb_base  = wb_block * self.block_size
            for i in range(self.block_size):
                self.next.write_byte(wb_base + i, victim['data'][i])

        # fetch block from next level
        for i in range(self.block_size):
            victim['data'][i] = self.next.read_byte(base + i)

        # load new block into cache
        victim['tag']   = tag
        victim['valid'] = True
        victim['dirty'] = False

        return victim['data'][offset]

    def write_byte(self, addr, val):
        set_idx, tag, offset, base = self._loc(addr)

        # hit
        for line in self.sets[set_idx]:
            if line['valid'] and line['tag'] == tag:
                self.hits += 1
                line['data'][offset] = val
                line['dirty'] = True
                return

        # miss: bring in block then write
        self.misses += 1
        victim = self.sets[set_idx][0]

        # write back if needed
        if victim['valid'] and victim['dirty']:
            self.writebacks += 1
            wb_block = (victim['tag'] * self.num_sets + set_idx)
            wb_base  = wb_block * self.block_size
            for i in range(self.block_size):
                self.next.write_byte(wb_base + i, victim['data'][i])

        # fetch block
        for i in range(self.block_size):
            victim['data'][i] = self.next.read_byte(base + i)

        # load and write
        victim['tag']   = tag
        victim['valid'] = True
        victim['dirty'] = True
        victim['data'][offset] = val

class CacheHierarchy:
    def __init__(self,
                 l1_type, l1_size, l1_block,
                 l2_type, l2_size, l2_block,
                 memory: Memory):

        # Level 2 (only direct-mapped)
        if l2_type != 'direct':
            raise NotImplementedError("Only direct-mapped L2 supported")
        self.l2 = CacheLevel(l2_size, l2_block, assoc=1, next_level=memory)

        # Level 1 instruction + data caches
        assoc = 1 if l1_type == 'direct' else (l1_size // l1_block)
        self.l1_inst = CacheLevel(l1_size, l1_block, assoc, next_level=self.l2)
        self.l1_data = CacheLevel(l1_size, l1_block, assoc, next_level=self.l2)

    def fetch_word(self, addr):
        # little-endian 4-byte fetch through instruction cache
        b0 = self.l1_inst.read_byte(addr)
        b1 = self.l1_inst.read_byte(addr+1)
        b2 = self.l1_inst.read_byte(addr+2)
        b3 = self.l1_inst.read_byte(addr+3)
        return (b0 | (b1 << 8) | (b2 << 16) | (b3 << 24))

    def fetch_halfword(self, addr):
        # little-endian 2-byte fetch through instruction cache
        lo = self.l1_inst.read_byte(addr)
        hi = self.l1_inst.read_byte(addr+1)
        return lo | (hi << 8)

    def read_byte(self, addr):
        return self.l1_data.read_byte(addr)

    def write_byte(self, addr, val):
        self.l1_data.write_byte(addr, val)

    @property
    def l1_misses(self):
        return self.l1_inst.misses + self.l1_data.misses

    @property
    def l2_misses(self):
        return self.l2.misses

    @property
    def writebacks(self):
        return (self.l1_inst.writebacks +
                self.l1_data.writebacks +
                self.l2.writebacks)
