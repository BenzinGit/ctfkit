from core.paths import get_chain_artifacts_dir
from pathlib import Path
import shutil
import argparse


def run(args):
    from core.runner import run_module_by_name
    from core.target import load_current_profile, target_add_cred

    data, _ = load_current_profile()

    # -------------------------
    # Run module
    # -------------------------
    results = run_module_by_name("ad.gettgt", args.extra, data)

    # -------------------------
    # Find generated ccache
    # -------------------------
    ccache_files = list(Path(".").glob("*.ccache"))

    if not ccache_files:
        print("[-] No ticket generated")
        return

    latest = max(ccache_files, key=lambda f: f.stat().st_mtime)

    print(f"[+] Found TGT: {latest.name}")

    # -------------------------
    # Save to artifacts
    # -------------------------
    artifacts = get_chain_artifacts_dir(data["name"], "gettgt")

    # determine user
    target_user = None
    if results:
        for c in results:
            target_user = c.get("user")

    if not target_user:
        # fallback: derive from filename
        target_user = latest.stem

    artifact_path = artifacts / f"{target_user}.ccache"

    shutil.move(str(latest), str(artifact_path))

    print(f"[+] Stored ticket: {artifact_path}")

    # -------------------------
    # Add credential
    # -------------------------
    target_add_cred(argparse.Namespace(
        user=target_user,
        password=None,
        hash=None,
        aes=None,
        ccache=str(artifact_path)
    ))