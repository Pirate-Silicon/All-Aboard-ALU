# Git and GitHub Basics

Git keeps a history of every version of your files, so you can always get
back to one that worked. GitHub is a website that hosts git repositories
online. Version control is ubiquitous in virtually every field in EECS; every industry team in hardware of software engineering uses git. If you don't already know how to use it, now's a perfect time to get familiar.

## One-time setup

1. **Make a GitHub account** at [github.com](https://github.com). Use a username you'd be fine putting on a résumé.
2. **Fork this repository.** On the repo's GitHub page, click **Fork** (top right), then **Create fork**. You now have your own copy at `github.com/<you>/All-Aboard-ALU`. You can change anything in it without affecting anyone else.
3. **Configure your git account** In a terminal, run:

   ```bash
   git config --global user.name  "Your Name"
   git config --global user.email "you@example.com"
   ```

4. **Clone your fork** onto your computer. In VS Code: **View > Command Palette** (Ctrl-Shift-P, or just F1), type `Git: Clone`, paste `https://github.com/<you>/All-Aboard-ALU.git`, and pick a folder. Or, in a terminal:

   ```bash
   git clone https://github.com/<you>/All-Aboard-ALU.git
   ```

Then go to [setup.md](setup.md) to open it in the container.

## The everyday loop

You change some files. Then:

```bash
git status                      # see what changed
git add model/alu_model.py      # pick which files to add to your commit
git commit -m "step 1: model passes all 40 checks"
git push                        # send it up to your fork on GitHub
```

- **`git status`** is always safe to run. If you're ever unsure about what's changed, run it
- **`git add`** chooses what goes into the next snapshot/changelog
- **`git commit`** takes the snapshot. Try to be as descriptive as possible in your message; save your future self time
- **`git push`** uploads your snapshots to GitHub, and establishes the new baseline for future changes to add onto

VS Code's Source Control panel (the branch icon on the left) does all of
this with buttons if you prefer. You can also install GitHub desktop to manage your commits, but it's not required.

A good habit: commit whenever something starts working. Then if you break
it, `git diff` shows exactly what you changed since it last worked.

## Getting updates

If the club fixes something in the original repo after you forked it, go to
your fork on GitHub and click **Sync fork**. Then pull the changes down:

```bash
git pull
```

This makes sure your copy of the repo is always up to date with the parent repo if anything changes.

## Want more?

Check out [The Missing Semester, lecture 6: Version Control](https://missing.csail.mit.edu/2020/version-control/), which explains how git actually works under the hood.
