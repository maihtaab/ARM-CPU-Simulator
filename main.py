# CP216 CPU Simulator Project by Maihtaab Sidhu #

from cpu import CPU
import config

if __name__ == "__main__":
    # Ask user for binary file name
    filename = input("Enter binary file name (e.g., test1.bin): ").strip()

    # Create CPU object
    cpu = CPU()

    # Load binary file into memory
    try:
        cpu.load_binary(filename)
    except FileNotFoundError:
        print(f"File '{filename}' not found. Please enter a binary file name that is in the same directory as this program and try again. :()")
        exit(1)

    # Run the program
    cpu.run()

    l1 = cpu.cache.l1_misses
    l2 = cpu.cache.l2_misses
    wb = cpu.cache.writebacks
    cost = 0.5 * l1 + l2 + wb
    print(f"\nRESULTS → L1 misses: {l1}, L2 misses: {l2}, writebacks: {wb}, cost: {cost}")
    
    # add to a CSV (for manual checks):
    # with open("results.csv","a") as f:
    #     f.write(f"{config.L1_BLOCK_SIZE},{config.L2_BLOCK_SIZE},{l1},{l2},{wb},{cost}\n")
