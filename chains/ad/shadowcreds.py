import argparse
import os
from pathlib import Path

from core.runner import run_module_by_name
from core.target import target_add_cred, load_current_profile


def run(args):
    data, _ = load_current_profile()

    results = run_module_by_name(
        "ad.shadowcreds",
        args.extra,
        data=data
    )

    if not results or not isinstance(results, list):
        print("[-] No valid results from shadowcreds")
        return

    # -------------------------
    # PRIORITY: NTLM > TICKET
    # -------------------------
    ntlm = next((c for c in results if c.get("type") == "hash"), None)
    ticket = next((c for c in results if c.get("type") == "ticket"), None)

    if ntlm:
        user = ntlm["user"]

        print(f"[+] Using NTLM for {user}")

        target_add_cred(argparse.Namespace(
            user=user,
            password=None,
            hash=ntlm["hash"],
            aes=None,
            ccache=None
        ))

    elif ticket:
        user = ticket["user"]
        ccache = ticket["ccache"]

        print(f"[+] Using ticket for {user}")

        target_add_cred(argparse.Namespace(
            user=user,
            password=None,
            hash=None,
            aes=None,
            ccache=ccache
        ))

        if ccache and Path(ccache).exists():
            os.environ["KRB5CCNAME"] = ccache
            print(f"[*] KRB5CCNAME={ccache}")

    # -------------------------
    # Reload profile
    # -------------------------
    new_data, _ = load_current_profile()
    return new_data