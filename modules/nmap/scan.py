def run(data, cred, args):
    import subprocess
    from pathlib import Path

    ip = data.get("ip")
    name = data.get("name")

    if not ip:
        print("[!] No IP set on target")
        return

    scan_dir = Path("scans")
    scan_dir.mkdir(exist_ok=True)

    output_base = scan_dir / name

    # ---------------- MODES ----------------
    mode = args.extra[0] if args.extra else "default"

    if mode == "fast":
        cmd = f"nmap -T4 -F -oA {output_base}_fast {ip}"

    elif mode == "full":
        cmd = f"nmap -p- -T4 -oA {output_base}_full {ip}"

    else:
        cmd = f"nmap -sC -sV -oA {output_base} {ip}"

    print(f"[*] Running: {cmd}\n")

    subprocess.run(cmd, shell=True)
