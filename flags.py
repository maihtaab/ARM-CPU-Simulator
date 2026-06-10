def set_flags(f, res, carry=None, overflow=None):
    f["Z"] = int(res == 0)
    f["N"] = (res >> 31) & 1
    if carry is not None:
        f["C"] = int(carry)
    if overflow is not None:
        f["V"] = int(overflow)