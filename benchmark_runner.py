import os

import config
from cpu import CPU

# binaries to test
binaries = ["test1.bin", "test2.bin", "test3.bin", "test4.bin"]

# cache parameters
l1_types        = ["direct", "fully_assoc"]
l1_block_sizes  = [4, 8, 16, 32]
l2_block_sizes  = [16, 32, 64]

results = []

# run every combination
for binfile in binaries:
    if not os.path.exists(binfile):
        print(f"Warning: {binfile} not found, skipping")
        continue

    for l1_type in l1_types:
        config.L1_TYPE = l1_type
        for l1_bs in l1_block_sizes:
            config.L1_BLOCK_SIZE = l1_bs
            for l2_bs in l2_block_sizes:
                config.L2_BLOCK_SIZE = l2_bs

                cpu = CPU()
                cpu.load_binary(binfile)
                cpu.run()

                l1 = cpu.cache.l1_misses
                l2 = cpu.cache.l2_misses
                wb = cpu.cache.writebacks
                cost = 0.5 * l1 + l2 + wb

                results.append((binfile, l1_type, l1_bs, l2_bs, l1, l2, wb, cost))
                print(f"[{binfile}] L1={l1_type}/{l1_bs}B  L2={l2_bs}B  cost={cost:.1f}")

# write to a CSV file
outname = "benchmark_results.csv"
with open(outname, "w") as f:
    f.write("binary,L1_type,L1_block,L2_block,l1_misses,l2_misses,writebacks,cost\n")
    for row in results:
        f.write(",".join(map(str, row)) + "\n")

print(f"\nDone. All results saved in {outname}")
