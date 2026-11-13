import sys

def brute(inp):
    import sys
    if hasattr(sys, 'set_int_max_str_digits'):
        sys.set_int_max_str_digits(0)
    a, b = inp.split()[:2]
    return str(int(a) + int(b))


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
