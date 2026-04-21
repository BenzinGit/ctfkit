# chains/ad/getst.py
from core.paths import get_chain_artifacts_dir
from pathlib import Path
import shutil
import argparse


def run(args):
    from core.runner import run_module_by_name
    from core.target import load_current_profile, target_add_cred
    import argparse

    data, _ = load_current_profile()

    results = run_module_by_name("ad.getst", args.extra, data)

    # -------------------------
    # Find generated ccache
    # -------------------------
    ccache_files = list(Path(".").glob("*.ccache"))

    if not ccache_files:
        print("[-] No ticket generated")
        return

    latest = max(ccache_files, key=lambda f: f.stat().st_mtime)

    print(f"[+] Found ticket: {latest.name}")

    # -------------------------
    # Save to artifacts
    # -------------------------
    artifacts = get_chain_artifacts_dir(data["name"], "getst")

    for c in results:
        target_user = c["user"]

    artifact_path = artifacts / f"{target_user}.ccache"
    
    shutil.move(str(latest), str(artifact_path))

    print(f"[+] Stored ticket: {artifact_path}")

    # -------------------------
    # Add credential
    # -------------------------
    target_add_cred(argparse.Namespace(
        user="Administrator",
        password=None,
        hash=None,
        aes=None,
        ccache=str(artifact_path)
    ))