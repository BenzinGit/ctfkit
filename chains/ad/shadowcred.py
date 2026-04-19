import argparse
import os
from core.target import target_add_cred, set_kerberos_env
from module.shadowcred import run as run_shadow_module

def run(data, cred, args):
    # 1. Run the module to get the ticket
    ccache_path = run_shadow_module(data, cred, args)

    if ccache_path:
        target_user = args.extra[0]
        
        # 2. Update the database (JSON)
        target_add_cred(
            argparse.Namespace(
                user=target_user,
                password=None,
                hash=None,
                aes=None,
                ccache=ccache_path
            )
        )
        
        # 3. Load into current session (The "export" part)
        set_kerberos_env(ccache_path)
    
    # Reload and return data
    from core.target import load_current_profile
    new_data, _ = load_current_profile()
    return new_data


def set_kerberos_env(ccache_path):
    """Sets the KRB5CCNAME environment variable for the current process."""
    if ccache_path and Path(ccache_path).exists():
        os.environ["KRB5CCNAME"] = str(ccache_path)
        print(f"[*] Environment: export KRB5CCNAME={ccache_path}")
    else:
        print("[!] Warning: Could not set KRB5CCNAME, file missing")

