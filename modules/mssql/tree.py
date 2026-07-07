from pathlib import Path
import subprocess

def run(data, cred, args):
    ip = data.get("ip")
    domain = data.get("domain", "")
    quiet = getattr(args, "quiet", False)

    if not ip:
        print("[!] Target IP required")
        return

    if not cred:
        print("[!] Credentials required")
        return

    user = cred.get("user")
    password = cred.get("secret")

    if not user or not password:
        print("[!] Invalid credentials")
        return

    # ---------------- PATH HANDLING ----------------
    # default: list root
    path = args.extra[0] if getattr(args, "extra", None) else "C:\\"

    # normalize slashes
    path = path.replace("/", "\\")

    # if not absolute, assume C:\
    if not path.lower().startswith(("c:\\", "d:\\", "\\\\")):
        path = f"C:\\{path}"

    # escape for SQL
    sql_path = path.replace("\\", "\\\\")
    query = f"EXEC master..xp_dirtree '{sql_path}', 1, 1"

    # ---------------- AUTH ----------------
    if getattr(args, "windows_auth", False):
        target = f"{domain}/{user}:{password}@{ip}"
        auth_flag = "-windows-auth"
    else:
        target = f"{user}:{password}@{ip}"
        auth_flag = ""

    cmd = ["impacket-mssqlclient", target]
    if auth_flag:
        cmd.append(auth_flag)

    print(f"[*] Target: {ip}")
    print(f"[*] Path: {path}")
    print(f"[*] Running xp_dirtree...\n")
    print(query)
    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        output, err = proc.communicate(query + "\nexit\n")

        # ---------------- PARSE OUTPUT ----------------
        lines = []
        capture = False

        for line in output.splitlines():
            if "subdirectory" in line.lower():
                capture = True
                continue

            if capture and line.strip():
                parts = line.split()
                if parts:
                    lines.append(parts[0])

        # ---------------- DISPLAY ----------------
        if lines:
            print("[+] Directory listing:\n")
            for l in lines:
                print(f"  {l}")
        else:
            print("[!] No results or access denied")

    except KeyboardInterrupt:
        print("\n[*] Interrupted.")