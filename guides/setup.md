# Setup

Every tool in this program runs on Linux. Rather than have you install twenty
tools one at a time, they all come packaged in one container: a small,
self-contained Linux computer that runs inside your own, with everything
already installed and set up. VS Code connects to it, so it feels like
normal VS Code, except the terminal is Linux and every tool you need is there.

**You'll need:**

- about 25 GB of free disk space (a 4 GB download that unpacks to about 17 GB)
- at least 8 GB of RAM (16 GB preferred)
- Windows 10 or 11, macOS, or Linux

---

## 1. Install Docker Desktop

Docker is what runs the container.

**Windows:**

1. Open PowerShell as Administrator: right-click the Start button, then Terminal (Admin).
2. Run `wsl --install` and restart when it asks. This installs WSL, the part of Windows that runs Linux. Docker needs it.
3. Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop/) and install it. Keep the default Use WSL 2 option checked.
4. Start Docker Desktop

**Mac:** download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop/). Pick Apple silicon or Intel to match your Mac ( > About This Mac). Install and start it.

**Linux:** install Docker Engine for your distribution ([docs.docker.com/engine/install](https://docs.docker.com/engine/install/)), then add yourself to the `docker` group: `sudo usermod -aG docker $USER`, then log out and back in.

**Check:** Docker Desktop's window says the engine is running (a green
indicator, bottom left)

## 2. Install VS Code and two extensions

1. Install **VS Code** from [code.visualstudio.com](https://code.visualstudio.com/).
2. Install **Git** from [git-scm.com](https://git-scm.com/downloads) if you don't have it
3. In VS Code, open the Extensions panel and install **Dev Containers**

## 3. Open your fork in the container

You should already have a fork. If not, do the first two steps of
[git-basics.md](git-basics.md) first.

1. In VS Code: **View > Command Palette** (Ctrl-Shift-P, or just F1)
2. Type `Dev Containers: Clone Repository in Container Volume` and pick it.
3. Paste your fork's URL: `https://github.com/<you>/All-Aboard-ALU`
4. **Wait.** The first time, Docker downloads the 4 GB image. That can take 10–30 minutes depending on your internet, and the bottom-right corner shows progress. Every time after this, it opens in seconds.

When it's done, VS Code shows the repo's files on the left, and the
bottom-left corner says **Dev Container: All-Aboard-ALU**.

Why the container? It keeps your files on Linux, inside Docker,
instead of on your computer's own drive. That makes every tool much faster
and avoids Windows-only problems. Your work is still saved
between sessions, and `git push` still sends it to your fork.

<details>
<summary>Prefer to have the files on your own drive?</summary>

Clone your fork normally (see [git-basics.md](git-basics.md)), open the folder
in VS Code, then run **Dev Containers: Reopen in Container** from the Command
Palette. Everything works, but on Windows the tools run slower, and
`chmod +x` will say "Operation not permitted". Scripts still run anyway, so
you can ignore that message.

</details>

## 4. Check that it works

Open a terminal in VS Code with Ctrl + \` (backtick). It's a Linux
terminal inside the container. It should print a few `[INFO]` lines when it starts

Paste this in and press Enter:

```bash
echo "PDK: $PDK"; python3 -c "import cocotb; print('cocotb', cocotb.__version__)"; iverilog -V 2>/dev/null | head -1; verilator --version; yosys -V; librelane --version | head -1
```

You should see something like:

```
PDK: sky130A
cocotb 2.1.0
Icarus Verilog version 14.0 (devel) (s20260301-579-g15d870a5-dirty)
Verilator 5.052 2026-09-05 rev v5.052
Yosys 0.70 (git sha1 28ba3cb92, Release, GNU /usr/bin/c++ 13.3.0)
LibreLane v3.1.0.dev3
```

The exact version numbers don't matter. What matters is that every line
prints a version and the first line says `sky130A`.

Then run the model checker:

```bash
cd model
python3 check_model.py
```

It's supposed to fail right now; you haven't written the model yet.
What matters is that it runs and prints a report.

## 5. The desktop, for tools with windows

Most tools in this program run in the terminal. A few (KLayout, the OpenROAD
GUI) open real windows. Those appear on a Linux desktop that runs inside the
container, which you view in a web browser tab.

1. In VS Code, open the **Ports** tab (next to Terminal at the bottom).
2. Find the row labelled **Desktop (GUI tools)**. Hover over its **Forwarded Address** and click the globe icon to open it in your browser.
3. On the page that opens, click **Connect**. The password is **`abc123`**.

To skip the password prompt, add this to the end of the address:
`/?password=abc123&autoconnect=true&resize=remote`.

You'll see a Linux desktop. Leave that tab open. Any GUI tool you start
from the VS Code terminal appears there.

Try it:

```bash
xeyes &
```

A pair of eyes should appear on the desktop and follow your mouse. Close it
when you're done.

Waveforms are different: they open right inside VS Code, with no desktop
needed. See [waveforms.md](waveforms.md).

## Every time after this

1. Start Docker Desktop (it can be set to start with your computer).
2. Open VS Code. Under **File > Open Recent**, pick the entry ending in **[Dev Container]**.

## Removing it all later

In Docker Desktop: **Containers**, delete the `All-Aboard-ALU` one; **Images**,
delete `hpretl/iic-osic-tools-devcontainer`; **Volumes**, delete the one
named after the repo (push your work first!). Then uninstall Docker Desktop
as normal.

## Where the tools come from

The container is [IIC-OSIC-TOOLS](https://github.com/iic-jku/IIC-OSIC-TOOLS),
maintained at Johannes Kepler University Linz, and used by universities
around the world for open-source chip design. Its exact version is pinned in
[.devcontainer/devcontainer.json](../.devcontainer/devcontainer.json), so
everyone has the same tools.

The same container setup also works in **GitHub Codespaces** (on your fork's
GitHub page: **Code > Codespaces > Create codespace**), which runs it in the
cloud instead of on your laptop. That's handy if your computer can't run
Docker, but the free monthly hours run out quickly with tools this size.
