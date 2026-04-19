import subprocess
from pathlib import Path
import argparse
from core.target import target_add_cred


def run(data, cred, args):
    """
    Authenticate via SMB using netexec

    Usage:
        ctf auth.smb
        ctf auth.smb user pass
        ctf auth.smb users.txt passwords.txt
    """

    extra = getattr(args, "extra", []) or []

    ip = data.get("ip")
    domain = data.get("domain")

    if not ip:
        print("[-] Target missing IP")
        return data

    cmd = ["netexec", "smb", ip]

    # -------------------------
    # Mode 1: No args → current cred
    # -------------------------
    if len(extra) == 0:
        if not cred:
            print("[-] No active credential")
            return data

        user = cred.get("user")
        password = cred.get("secret")

        if not user or not password:
            print("[-] Current credential not usable")
            return data

        cmd += ["-u", user, "-p", password]

    # -------------------------
    # Mode 2: user/pass or files
    # -------------------------
    elif len(extra) >= 2:
        user_input = extra[0]
        pass_input = extra[1]

        user_path = Path(user_input)
        pass_path = Path(pass_input)

        # spray mode
        if user_path.exists() and pass_path.exists():
            cmd += ["-u", str(user_path), "-p", str(pass_path)]

        # single credential
        else:
            cmd += ["-u", user_input, "-p", pass_input]

    else:
        print("[-] Usage: ctf auth.smb user pass OR users.txt passwords.txt")
        return data

    if domain:
        cmd += ["-d", domain]

    print(f"[*] Running: {' '.join(cmd)}")

    # -------------------------
    # Run (preserve colors)
    # -------------------------
    subprocess.run(cmd)
    
    if len(extra) == 0:
        return
    
    # -------------------------
    # Run again (capture for parsing)
    # -------------------------
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    output = result.stdout + result.stderr

    # -------------------------
    # Parse valid creds
    # -------------------------
    valid = []

    for line in output.splitlines():
        if "[+]" in line and "\\" in line and ":" in line:
            try:
                part = line.split()[-1]  # domain\user:pass
                domain_user, password = part.split(":", 1)

                if "\\" in domain_user:
                    user = domain_user.split("\\")[1]
                else:
                    user = domain_user

                valid.append((user, password))
            except:
                continue

    if not valid:
        print("[-] No valid credentials found")
        return data

    print("\n[+] Valid credentials:\n")

    current_user = cred.get("user") if cred else None

    for user, password in valid:
        print(f"[+] {user}:{password}")

        # Skip if already current credential
        if user == current_user:
            print("[*] Already active credential")
            continue

        target_add_cred(
            argparse.Namespace(
                user=user,
                password=password,
                hash=None,
                aes=None,
                ccache=None
            )
        )


    # -------------------------
    # Switch to new credential
    # -------------------------
    from core.target import target_set_cred

    target_set_cred(
        argparse.Namespace(
            identifier=user
        )
    )

    from core.target import load_current_profile

    data, _ = load_current_profile()
    return data


    return data