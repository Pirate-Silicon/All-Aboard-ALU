# Step 1: The Spec, and a Model of It

**Goal:** Know exactly what the ALU does for every possible input, before you
write any hardware, by writing it as a Python program.

## First: start the setup download

Open [guides/setup.md](../guides/setup.md) and get through the install steps
now. The tools are a 4 GB download, so start it and watch the videos below
while it runs. You only need Python for this step, but everything after this
needs the full setup

## Watch and read

1. **[Crash Course Computer Science #5: How Computers Calculate, the ALU](https://www.youtube.com/watch?v=1I5ZMmrOfnA)**. Great introduction; start here
2. **Harris & Harris videos on binary numbers.** Skip any you already know:
   - [1.2 Unsigned Binary Numbers](https://youtu.be/IurbwMTfw5E)
   - [1.3 Hexadecimal Numbers](https://youtu.be/OQV4QhoOQig)
   - [1.5 Binary Addition](https://youtu.be/Abz1HMfwFE8)
   - [1.6 Signed Numbers](https://youtu.be/wyDPuw25kg8). This one matters most: two's complement is how the ALU handles negatives values
3. **Harris & Harris videos on the ALU itself:**
   - [5.6 Subtractors & Comparators](https://youtu.be/ZbZ33tj-ncg)
   - [5.7 Arithmetic Logic Units](https://youtu.be/WXMf0y4NoBw). This is the ALU our spec is based on. It might seem a little overwhelming at first, but you'll understand every part after working through the next couple of steps.
4. **[SPEC.md](SPEC.md)**, the spec. Read all of it; it's short, and every later step is checked against it

**Extra:**

- [Ben Eater's ALU](https://eater.net/8bit/alu), from his 8-bit breadboard computer series. He builds an ALU out of real chips and wires. Also check out his [YouTube channel](https://www.youtube.com/@BenEater), which has a bunch of other helpful walkthroughs/guides
- [Ken Shirriff on the 74181](https://www.righto.com/2017/03/inside-vintage-74181-alu-chip-how-it.html). The 74181 was a real 4-bit ALU on a single chip, from 1970: the same size as ours. Shirriff photographs the silicon and explains how it works.
- [Harris & Harris 6.8 Branches](https://youtu.be/npONPosFIDA). How a RISC-V program decides which way to go, which is what the flags are for.

## Background

### What an ALU is

The **arithmetic logic unit** is the part of a processor that actually
computes. Everything else (fetching instructions, decoding them, reading
registers) exists to feed it the right two numbers and the right operation,
then put its answer somewhere useful.

You give it two inputs, `a` and `b`, plus an opcode saying which
operation to do. It gives back a result, plus a few flags, which are single-bit fields
that describe the result.

### Where ALUs are used

Everywhere:

- Every core in your laptop has several, so it can do several operations at once
- A GPU has thousands
- The microcontroller in your microwave has one
- Inside a processor, the ALU also computes memory addresses (`base + offset`, for example)
- It also decides branches. Your `if (a < b)` compiles down to the ALU subtracting `b` from `a`, and a branch looking at the flags; [SPEC.md](SPEC.md) has the table

### Four bits, two readings

A 4-bit pattern can be read two ways, and the ALU serves both:

| Bits   | Unsigned | Signed (two's complement) |
| ------ | -------- | ------------------------- |
| `0000` | 0        | 0                         |
| `0001` | 1        | 1                         |
| `0111` | 7        | 7                         |
| `1000` | 8        | −8                        |
| `1001` | 9        | −7                        |
| `1110` | 14       | −2                        |
| `1111` | 15       | −1                        |

The trick that makes two's complement worth it: binary addition gives the
right bits for both readings. `1111 + 0001 = 0000` unsigned is 15 + 1 = 16, which doesn't fit within 4 bits and gets read as 0, which is exactly what we'd expect from the signed interpretation of -1 + 1. The key is that the hardware can't tell whether the numbers are signed or not; that distinction is made by the programmer.

The flags tell the two readings apart:

- **C** says the _unsigned_ answer didn't fit.
- **V** says the _signed_ answer didn't fit.

### Why 4 bits

Big enough to be real, small enough to know completely. The whole ALU has
8 opcodes × 16 values of `a` × 16 values of `b` = 2048 possible inputs.
By the end of this step you shoud've printed every one of them. A 64-bit ALU
has about 10<sup>39</sup>. Testing a billion per second, that would take
about 10<sup>13</sup> times the age of the universe. How you test hardware
you can't test completely is what step 3 is about.

### Why write a model first

Writing the model
forces you to decide every small question the spec might leave open, before
you've spent any effort on hardware. In step 3, this exact file becomes the
reference model your testbench uses to decide if the hardware is right.
Professional verification teams work the same way, and their models are very
often in Python too.

### Python, if you know Java

- No braces and no semicolons. Indentation is the block structure, so be consistent.
- No type declarations: `full = a + b`, not `int full = a + b;`.
- `elif`, not `else if`
- `and`, `or`, `not`, not `&&`, `||`, `!`
- Python integers also never overflow. `15 + 15` is 30, which doesn't wrap. That's why the model masks with `& MASK` to throw away anything past 4 bits, which is what the hardware does.
- **`~b` doesn't stay in 4 bits.** Python's `~5` is `-6`. That's the right value in two's complement, but Python stores it with infinitely many 1s in front, not as the 4-bit pattern `1010`. The model keeps every value as 0 to 15, like the hardware's 4 wires, so mask it: `~b & MASK` gives `1010`, which is 10 (unsigned). Skip the mask and `y` still comes out right, but the carry doesn't.

If you've never written any python code: work through sections 3 and 4 of the
[official Python tutorial](https://docs.python.org/3/tutorial/) first

## Do

### 1. Answer these from the spec

Work each one out by hand, in binary, before you open the answers. These are
exactly the questions your model has to get right.

1. What is ADD 7 + 1? Give `y` and all four flags.
2. What is SUB 0 − 1?
3. Why does SUB 5 − 3 set C = 1?
4. What is SHR applied to `1000`? Is the answer still negative?
5. What is ADD 15 + 1? Explain C and V by reading the inputs both unsigned and signed.
6. Right after reset, `y` is `0000`. Is Z 1 or 0? Why?
7. You apply ADD 2 + 3 just before edge 1, and SUB 9 − 1 just before edge 2. What's on `y` after edge 2? After edge 3?

<details>
<summary>Answers</summary>

1. `0111 + 0001 = 1000`. y = 8 (signed: −8). N = 1, Z = 0, C = 0, **V = 1**: two positives made a negative.
2. `0000 + 1110 + 1 = 1111`. y = 15 (signed: −1). N = 1, Z = 0, **C = 0** because 0 < 1 unsigned (a borrow), V = 0.
3. `0101 + 1100 + 1 = 1 0010`. The adder's carry out is 1, and for SUB, C = 1 means there was no borrow: 5 ≥ 3.
4. `0100`, which is +4. SHR is a _logical_ shift: a 0 comes in at the top, so the sign is lost. (An _arithmetic_ shift would copy the sign bit in and give `1100`, which is −4. Our spec says logical.)
5. `1111 + 0001 = 1 0000`. y = 0, Z = 1, N = 0. Unsigned, 15 + 1 = 16 doesn't fit in 4 bits, so **C = 1**. Signed, −1 + 1 = 0 fits fine, so **V = 0**.
6. **0.** Reset clears every register, flags included. Nothing has been computed yet, so there's nothing for Z to describe.
7. After edge 2, y = 5 (2 + 3). After edge 3, y = 8 (9 − 1). One answer per cycle, each two edges behind its inputs.

</details>

### 2. Draw the timing

On paper, extend the timing table in [SPEC.md](SPEC.md) to five clock edges,
with three different operations applied back to back. For each edge, write
what's in the input registers and what's on `y`. You'll compare it to a real
waveform in step 2.

### 3. Write the model

Open [model/alu_model.py](../model/alu_model.py). ADD is done for you as the
worked example. Fill in every `TODO(step1)`.

Check it:

```bash
cd model
python3 check_model.py
```

You're looking for:

```
 MODEL PASSED, all 40 checks
```

Every failure line says which case failed, why that case is in the list, and
what you got versus what was expected. Fix one at a time.

### 4. See the whole thing

```bash
python3 check_model.py --table > table.csv
```

Open `table.csv` in VS Code. That's 2048 rows: every input this ALU will ever
see and exactly what it should do with each one. Scroll through the SUB rows
and watch C flip as `b` passes `a`. Delete the file when you're done (it's
easy to regenerate).

## Check yourself

- `check_model.py` passes all 40 checks.
- You can explain, without looking, why SUB 3 − 5 sets C = 0.
- You can say why C and V are two different flags.

## Stuck?

| What you see                           | What's wrong                                                                                                                        |
| -------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `python3: command not found`           | Your setup isn't finished, or you're on Windows outside the container. Try `python` or `py`, or finish [setup](../guides/setup.md). |
| SUB gives a negative `y`, like −2      | You used `~b` without masking. `(~b & MASK)`.                                                                                       |
| NOT gives a negative `y`               | Same thing: `~a & MASK`.                                                                                                            |
| SHL gives 18                           | You forgot to mask: `(a << 1) & MASK`.                                                                                              |
| Every flag test fails but `y` is right | You left `n = 0` and `z = 0` at the bottom.                                                                                         |
| `IndentationError`                     | Python cares about spaces. Make every line in a block line up exactly.                                                              |
