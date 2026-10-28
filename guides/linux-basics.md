# Linux Command Line Basics

Every chip design tool runs on Linux and is driven from a terminal. The
container you set up in [setup.md](setup.md) is a Linux machine, and the
terminal panel at the bottom of VS Code is how you access it

## The prompt

When the terminal is waiting for you, it shows a **prompt**, something like:

```
username@machine:/workspaces/All-Aboard-ALU$
```

The part after the `:` is where you are: your current directory (folder).
You type a command, press Enter, and it runs there.

## Moving around

| Command | What it does                                                             |
| ------- | ------------------------------------------------------------------------ |
| `pwd`   | print working directory: where am I?                                     |
| `ls`    | list the items in the current directory                                  |
| `ls -l` | the same, with sizes and dates                                           |
| `cd tb` | go into the folder called `tb`                                           |
| `cd ..` | go up one folder (`..` always means "the folder above/parent directory") |
| `cd ~`  | go to your home folder                                                   |
| `cd -`  | go back to wherever you just were                                        |

A path is directions to a file. `../rtl/alu.sv` means "go up one folder,
then into `rtl`, then the file `alu.sv`". In this program, every step's
instructions say which folder to be in. If a command can't find a file,
`pwd` is the first thing to check.

## Looking at files

| Command             | What it does                                                                             |
| ------------------- | ---------------------------------------------------------------------------------------- |
| `cat file`          | print the whole file (short for concatenate)                                             |
| `less file`         | page through a long file. Arrow keys or space to scroll, `/word` to search, `q` to quit. |
| `head -20 file`     | the first 20 lines                                                                       |
| `tail -20 file`     | the last 20 lines                                                                        |
| `grep word file`    | print only the lines containing `word`                                                   |
| `grep -n word file` | the same, with line numbers                                                              |

To edit a file, open it in VS Code: click it in the file explorer on the
left, or type `code file` in the terminal. Vim is cool, but unnecessary.

## Making and moving things

| Command          | What it does                                 |
| ---------------- | -------------------------------------------- |
| `mkdir <name>`   | make a folder                                |
| `cp <from> <to>` | copy a file                                  |
| `mv <from> <to>` | move or rename a file                        |
| `rm <file>`      | delete a file. note: there is no recycle bin |

## Running things

| What you type     | What it does                                                               |
| ----------------- | -------------------------------------------------------------------------- |
| `make smoke`      | runs the recipe called `smoke` from the `Makefile` in this folder          |
| `./run`           | runs the script called `run` in this folder. The `./` means "this folder". |
| `chmod +x run`    | marks `run` as allowed to execute. Do this once after creating a script.   |
| `python3 file.py` | runs a Python program                                                      |

## Four habits that save hours

1. **Tab completes.** Type `cd st` and press Tab: it fills in `step`. Press Tab twice to see every option. It's faster, and it stops typos.
2. **The up arrow** brings back your last command. Press it again for the one before that. Edit it and press Enter.
3. **Ctrl-C stops** whatever is running. A program that seems stuck, or a test that won't end: Ctrl-C.
4. **Read the first error, not the last.** When something fails, tools often print dozens of lines. The first error is usually the real problem, and everything after it is the fallout.

## Reading an error message

```
../rtl/alu_core.sv:47: syntax error
```

That's file, line number, and what went wrong. Open the file, go to that line
(`Ctrl-G` in VS Code), and look at it.

If you can't make sense of an error, copy the exact text and paste it into a
search engine/AI or ask someone

## Want more?

[The Missing Semester](https://missing.csail.mit.edu/), MIT's course on tools
CS classes forget to teach. Lecture 1, "The Shell", covers all of this in more
depth
