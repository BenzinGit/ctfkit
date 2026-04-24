def run(data, cred, args):
    from argparse import Namespace
    from modules.exec.win import run as exec_win

    # ---------------- VALIDATION ----------------
    user = cred.get("user")

    if not user:
        print("[!] No valid credential selected")
        return data

    # ---------------- COMMAND ----------------
    cmd = fr"type C:\Users\{user}\Desktop\user.txt"

    print("[*] Attempting to retrieve root flag for current user...\n")

    # reuse exec.win
    exec_win(data, cred, Namespace(cmd=cmd))

    return data
