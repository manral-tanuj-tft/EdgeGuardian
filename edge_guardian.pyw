#!/usr/bin/env pythonw
"""
Edge Guardian (silent) - kills background Edge processes when no Edge window
is open. Designed to run via pythonw.exe (no console) at login.

Logs to %LOCALAPPDATA%\\EdgeGuardian\\guardian.log so you can check it if needed.

Tip: you may not even need this. In Edge, open edge://settings/system and
turn off "Startup boost" and "Continue running background extensions and
apps when Microsoft Edge is closed".
"""
import ctypes
import ctypes.wintypes as wt
import os
import subprocess
import sys
import time

USER32 = ctypes.windll.user32
KERNEL32 = ctypes.windll.kernel32

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
EnumWindowsProc = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

# --- where to keep our state (log + single-instance lock) ---
APP_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
                       "EdgeGuardian")
os.makedirs(APP_DIR, exist_ok=True)
LOG_PATH = os.path.join(APP_DIR, "guardian.log")


def log(msg):
    """Append a timestamped line to the log file (silent, no console)."""
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(time.strftime("%Y-%m-%d %H:%M:%S  ") + msg + "\n")
    except Exception:
        pass


def ensure_single_instance():
    """Use a named Windows mutex so a second login launch just exits quietly."""
    mutex = KERNEL32.CreateMutexW(None, False, "Global\\EdgeGuardianSingleton")
    ERROR_ALREADY_EXISTS = 183
    if KERNEL32.GetLastError() == ERROR_ALREADY_EXISTS:
        sys.exit(0)
    return mutex  # keep a reference alive for the process lifetime


def _process_exe_name(pid):
    handle = KERNEL32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not handle:
        return ""
    try:
        buf_len = wt.DWORD(1024)
        buf = ctypes.create_unicode_buffer(buf_len.value)
        if KERNEL32.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(buf_len)):
            return buf.value.rsplit("\\", 1)[-1].lower()
        return ""
    finally:
        KERNEL32.CloseHandle(handle)


def is_edge_window_open():
    """True if any *visible* top-level window belongs to msedge.exe."""
    found = {"edge": False}

    def callback(hwnd, lparam):
        if not USER32.IsWindowVisible(hwnd):
            return True
        pid = wt.DWORD()
        USER32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value and _process_exe_name(pid.value) == "msedge.exe":
            found["edge"] = True
            return False
        return True

    USER32.EnumWindows(EnumWindowsProc(callback), 0)
    return found["edge"]


def edge_processes_exist():
    result = subprocess.run(
        ["tasklist", "/FI", "IMAGENAME eq msedge.exe", "/NH"],
        capture_output=True, text=True,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    return "msedge.exe" in result.stdout.lower()


def kill_all_edge_processes():
    subprocess.run(
        ["taskkill", "/F", "/IM", "msedge.exe", "/T"],
        capture_output=True,
        creationflags=subprocess.CREATE_NO_WINDOW
    )


def main():
    _mutex = ensure_single_instance()  # noqa: F841 (kept alive intentionally)
    log("Edge Guardian started.")
    while True:
        try:
            if not is_edge_window_open() and edge_processes_exist():
                log("No Edge window found - killing background Edge processes.")
                kill_all_edge_processes()
            time.sleep(5)
        except Exception as e:
            log(f"Error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
