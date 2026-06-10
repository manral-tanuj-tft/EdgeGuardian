# Edge Guardian

A tiny background utility for Windows that **kills leftover Microsoft Edge
processes once you close every Edge window.** Edge often keeps processes
running in the background after you close it (Startup boost, background
extensions), which can eat memory and slow your PC down. Edge Guardian
watches for this and cleans them up automatically.

It runs silently — no console window, no taskbar icon — and starts itself at
every login. Set it up once and forget about it.

> **Before you install anything:** you may not need this at all. Open
> `edge://settings/system` in Edge and turn off **"Startup boost"** and
> **"Continue running background extensions and apps when Microsoft Edge is
> closed"**. That solves the same slowdown with zero moving parts. Use Edge
> Guardian only if those toggles aren't enough.

---

## How it works

Every 5 seconds the guardian asks two questions:

1. **Is a real Edge window open?**
   It enumerates all *visible* top-level windows on the desktop and, for each
   one, asks Windows which executable owns it. A window only counts if it
   belongs to `msedge.exe`. (This is why it doesn't get fooled by Chrome, VS
   Code, Discord, or other apps — they share Edge's window class but are
   different processes.)

2. **Are there any Edge processes running?**
   It checks `tasklist` for `msedge.exe`.

If **no Edge window is open** but **Edge processes still exist**, those are
leftover background processes — so it force-kills the whole `msedge.exe` tree
with `taskkill /F /T`. If you have an Edge window open, it does nothing.

Other details:

- **Silent:** the script is a `.pyw` file launched with `pythonw.exe`, so there
  is no console window. Status messages go to a log file instead (see below).
- **Single instance:** a named Windows mutex ensures only one copy ever runs,
  even if the launcher fires twice.
- **Low impact:** one lightweight window scan every 5 seconds.

---

## Files

| File | Purpose |
|------|---------|
| `edge_guardian.pyw` | The background script itself. |
| `install_edge_guardian_noadmin.bat` | One-time setup, **no admin needed**. Adds a hidden launcher to your Startup folder. |
| `install_edge_guardian.bat` | Alternative setup using Task Scheduler (**requires admin**). |

---

## Requirements

- Windows
- [Python 3](https://www.python.org/) installed, with **"Add Python to PATH"**
  ticked during installation. Verify by opening Command Prompt and running:
  ```
  pythonw --version
  ```

---

## Installation (no admin)

1. Put `edge_guardian.pyw` and `install_edge_guardian_noadmin.bat` together in
   a **permanent** folder, e.g. `C:\Tools\EdgeGuardian\`. (Don't use Downloads —
   the launcher points at this exact path.)
2. **Double-click** `install_edge_guardian_noadmin.bat`.
3. Done. It starts immediately and will auto-start at every login.

This writes a small `EdgeGuardian.vbs` into your personal Startup folder
(`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`). The VBS launches
`pythonw.exe` with window style `0` (fully hidden).

### Alternative: Task Scheduler (requires admin)

Right-click `install_edge_guardian.bat` → **Run as administrator**. This
registers a logon-triggered scheduled task named `EdgeGuardian` instead of
using the Startup folder.

---

## Checking it's running

- **Task Manager** → *Details* tab → look for `pythonw.exe`.
- **Log file:** `%LOCALAPPDATA%\EdgeGuardian\guardian.log` — shows when it
  started and each time it killed background processes.

---

## Removing it

**If you used the no-admin installer:** delete the launcher. Quick way — press
`Win+R`, type `shell:startup`, Enter, and delete `EdgeGuardian.vbs`. Then end
any running `pythonw.exe` in Task Manager (or just reboot).

**If you used the Task Scheduler installer:** open Command Prompt and run:
```
schtasks /Delete /TN "EdgeGuardian" /F
```

---

## Notes & caveats

- This runs only while **you** are logged in — not before login or while
  logged out. That's fine for the intended use.
- "Silent" means **no visible window** — not hidden from inspection. The task /
  startup entry and `pythonw.exe` are plainly visible in Task Scheduler, the
  Startup folder, and Task Manager. This is a personal utility for your own PC.
  On a shared or work machine, make sure you're allowed to add startup items.
- A force-kill can occasionally interrupt Edge mid-write (e.g. while it's saving
  session data right as you close it). The `edge://settings/system` toggles
  above avoid that risk entirely, which is why they're worth trying first.

---

## License

Do whatever you like with it.
