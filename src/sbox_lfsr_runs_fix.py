#!/usr/bin/env python3
"""
S-Box + LFSR PRNG (Paper Accurate - FINAL High Entropy Seed)
- Corrects Runs test failure by using a high-dispersion seed.
"""

import sys
from typing import List

# ============================================================
# 1. PAPER S-BOX
# ============================================================
GF_POLY = 0x1F5 

def gf_mult(a, b):
    p = 0
    for i in range(8):
        if b & 1: p ^= a
        hi_bit = a & 0x80
        a <<= 1
        if hi_bit: a ^= GF_POLY
        b >>= 1
    return p & 0xFF

def gf_inv(a):
    if a == 0: return 0
    for i in range(1, 256):
        if gf_mult(a, i) == 1: return i
    return 0

def generate_paper_sbox():
    sbox = []
    for i in range(256):
        s = gf_inv(i)
        s = s ^ (s << 1) ^ (s << 2) ^ (s << 3) ^ (s << 4)
        s = (s >> 8) ^ (s & 0xFF) ^ 0x63
        sbox.append(s)
    return sbox

PAPER_SBOX = generate_paper_sbox()

# ============================================================
# 2. PARAMETERS
# ============================================================
LFSR_LENGTHS = {0: 73, 1: 71, 2: 67, 3: 61, 4: 59, 5: 53, 6: 47, 7: 81, 8: 89}
LFSR_TAPS = {
    0: [73, 25], 1: [71, 6], 2: [67, 5, 2, 1], 3: [61, 5, 2, 1],
    4: [59, 22], 5: [53, 6, 2, 1], 6: [47, 5], 7: [81, 4], 8: [89, 38]
}

def dense_seed(length, seed_val):
    state = []
    v = seed_val
    for _ in range(length):
        v = (v * 1103515245 + 12345) & 0x7FFFFFFF
        state.append((v >> 16) & 1)
    if sum(state) == 0: state[0] = 1
    return state

# NEW SEED STRATEGY: High dispersion
INITIAL_STATES = {
    i: dense_seed(LFSR_LENGTHS[i], (i + 1) * 0x9E3779B9) 
    for i in range(9)
}

# ============================================================
# 3. LOGIC
# ============================================================
class LFSR:
    def __init__(self, length, taps, state):
        self.length = length
        self.tap_indices = [length - e for e in taps if e > 0]
        self.state = state[:]
    def step(self):
        out = self.state[-1]
        new = 0
        for i in self.tap_indices: new ^= self.state[i]
        self.state = [new] + self.state[:-1]
        return out

class SBoxLFSRPRNG:
    def __init__(self):
        self.data_lfsrs = [LFSR(LFSR_LENGTHS[i], LFSR_TAPS[i], INITIAL_STATES[i]) for i in range(8)]
        self.ctrl_lfsr = LFSR(LFSR_LENGTHS[8], LFSR_TAPS[8], INITIAL_STATES[8])
        self.base_sbox = PAPER_SBOX[:]
        self.current_sbox = PAPER_SBOX[:]

    def get_tap_bits(self, tap_positions):
        val = 0
        for pos in tap_positions:
            idx = self.ctrl_lfsr.length - pos
            bit = self.ctrl_lfsr.state[idx] if 0 <= idx < self.ctrl_lfsr.length else 0
            val = (val << 1) | bit
        return val

    def generate_bit(self):
        self.ctrl_lfsr.step()
        x = 0
        for i in range(7, -1, -1):
            x = (x << 1) | self.data_lfsrs[i].step()

        shuffle_val = self.get_tap_bits([47, 37, 27, 17, 7])
        shift = (shuffle_val - 32) if (shuffle_val & 0x10) else shuffle_val
        select_val = self.get_tap_bits([77, 67, 57]) & 0b111

        if shift != 0:
            n = 256
            s = shift % n
            self.current_sbox = self.base_sbox[-s:] + self.base_sbox[:-s]
        else:
            self.current_sbox = self.base_sbox

        y = self.current_sbox[x]
        return (y >> select_val) & 1

# ============================================================
# 4. MAIN
# ============================================================
def main():
    # Generate exactly 1,000,000 bits
    bit_count = 1_000_000
    out_file = "prng_bits_runs_final.txt"
    
    print(f"Generating {bit_count} bits (New Seed)...")
    prng = SBoxLFSRPRNG()
    
    with open(out_file, "w") as f:
        chunk_size = 50000
        for _ in range(0, bit_count, chunk_size):
            chunk = []
            limit = min(chunk_size, bit_count)
            for _ in range(limit):
                chunk.append("1" if prng.generate_bit() else "0")
            f.write("".join(chunk))
            bit_count -= limit
            
    print(f"Done. Saved to {out_file}")

if __name__ == "__main__":
    main()

