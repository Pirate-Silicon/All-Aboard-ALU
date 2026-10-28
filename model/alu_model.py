# TODO in step 1
#
# Write this python reference from step1-spec/SPEC.md and nothing else. In step 3, your testbench
# imports this exact file and uses it to decide whether the hardware is right
#
# Check your work with: python3 check_model.py


from dataclasses import dataclass

WIDTH = 4
MASK = (1 << WIDTH) - 1        # 0...000_1111: AND with this to keep a number inside 4 bits
SIGN = 1 << (WIDTH - 1)        # 0b1000: the sign bit; AND with this to determine whether a value is negative (1) 

# Opcodes, numbered exactly as in the spec
ADD, SUB, AND, OR, XOR, NOT, SHL, SHR = range(8) # = 0, 1, 2, etc.
OP_NAMES = ["ADD", "SUB", "AND", "OR", "XOR", "NOT", "SHL", "SHR"]


# Given. A small class that just holds the five outputs together.
# @dataclass makes it so two results with the same five values evaluate as 
# equal with ==. Step 3 relies on that
@dataclass(frozen=True)
class AluResult:
    y: int   # 4-bit result, 0-15 (unsigned)
    n: int   # 1 if y is negative when read as signed
    z: int   # 1 if y is zero
    c: int   # carry out of the adder (ADD and SUB only)
    v: int   # signed overflow (ADD and SUB only)


# Given. Handy for thinking and for debugging; you don't have to use it
def to_signed(x):
    """Read a 4-bit pattern as two's complement: 0b1111 -> -1, 0b0111 -> 7."""
    return x - (1 << WIDTH) if x & SIGN else x
  

def alu(op, a, b):
    """Compute one ALU operation. a and b are unsigned 4-bit ints, 0-15"""
    c = 0
    v = 0

    if op == ADD:
        # Worked example. Read it closely; the other seven follow the same shape.
        full = a + b                       # can be up to 5 bits wide (15 + 15 = 30)
        y = full & MASK                    # keep the low 4 bits
        c = full >> WIDTH                  # the 5th bit is the carry out
        # Overflow: both inputs had the same sign, and the result's sign differs.
        v = int((a & SIGN) == (b & SIGN) and (y & SIGN) != (a & SIGN)) # the inner expresion evaluates to a boolean; cast it to an integer to record v as 1 or 0 (t or f)

    elif op == SUB:
        # TODO(step1): compute a - b the way the hardware does, as a + ~b + 1.
        #
        # Careful: in Python, ~b is -(b + 1), a negative number, not a 4-bit
        # pattern. Mask it first: (~b & MASK). Then work out y and c the same
        # way ADD does. For v, the spec has the rule for SUB, and it is not
        # the same as the rule for ADD.
        y = 0

    # TODO(step1): the remaining six. Each is one line, y = ....
    # Two to think about:
    #   NOT  Python's ~ gives a negative number again. Mask it.
    #   SHL  a << 1 can produce a 5-bit number. Mask it.
    # The spec says what C and V are for these. Look at what this function
    # starts c and v at, and you may find there is nothing else to do.
    elif op == AND:
        y = 0
    elif op == OR:
        y = 0
    elif op == XOR:
        y = 0
    elif op == NOT:
        y = 0
    elif op == SHL:
        y = 0
    elif op == SHR:
        y = 0

    else:
        raise ValueError(f"opcode must be 0-7, got {op}")

    # TODO(step1): n and z. Both come from y alone, for every operation.
    n = 0
    z = 0
    return AluResult(y, n, z, c, v)
