import subprocess
from pathlib import Path
import os

DEFAULT_WORDLIST = "/usr/share/wordlists/rockyou.txt"
HASHCAT_MODE = "16900"

def run(data, cred, args):
    extra = getattr(args, "extra", []) or []
    if len(extra) < 1:
        print("[-] Missing vault file")
        return data

    vault_file = Path(extra[0]).expanduser()
    wordlist = Path(extra[1] if len(extra) >= 2 else DEFAULT_WORDLIST).expanduser()

    if not vault_file.exists():
        print(f"[-] Vault not found: {vault_file}")
        return data

    # 1. Split Multi-Vault File
    raw_content = vault_file.read_text()
    # Split by the header, but keep the header in the resulting strings
    vaults = ["$ANSIBLE_VAULT" + v for v in raw_content.split("$ANSIBLE_VAULT") if v.strip()]

    print(f"[*] Detected {len(vaults)} vault(s) in {vault_file.name}")

    for i, vault_data in enumerate(vaults):
        print(f"\n--- Processing Vault #{i+1} ---")
        
        # Create a temporary file for THIS specific vault
        v_tmp = Path(f"/tmp/vault_{i}.tmp")
        # Ensure it's sanitized (stripped lines)
        clean_v = "\n".join([line.strip() for line in vault_data.strip().splitlines()])
        v_tmp.write_text(clean_v)

        # 2. ansible2john
        try:
            proc = subprocess.run(["ansible2john", str(v_tmp)], capture_output=True, text=True)
            if proc.returncode != 0:
                print(f"[-] ansible2john failed for Vault #{i+1}")
                continue
            
            raw_hash = proc.stdout.strip()
            clean_hash = raw_hash.split(":", 1)[1] if ":" in raw_hash else raw_hash
            
            h_tmp = Path(f"/tmp/vault_{i}.hash")
            h_tmp.write_text(clean_hash)
        except Exception as e:
            print(f"[-] Error extracting hash #{i+1}: {e}")
            continue

        # 3. Hashcat
        crack_cmd = ["hashcat", "-m", HASHCAT_MODE, "-a", "0", str(h_tmp), str(wordlist), "--quiet"]
        subprocess.run(crack_cmd)

        # 4. Show & Decrypt
        show_proc = subprocess.run(crack_cmd + ["--show"], capture_output=True, text=True)
        password = show_proc.stdout.strip().split(":")[-1] if show_proc.stdout else None

        if password:
            print(f"[+] Password: {password}")
            
            decrypt_cmd = f"echo '{password}' | ansible-vault decrypt --vault-password-file /bin/cat {v_tmp} --output -"
            res = subprocess.run(decrypt_cmd, shell=True, capture_output=True, text=True)
            
            if res.returncode == 0:
                print(res.stdout) # Raw output
                print("")        # Force a newline so it doesn't look messy
            else:
                print(f"[-] Decrypt Error: {res.stderr.strip()}")

    return data