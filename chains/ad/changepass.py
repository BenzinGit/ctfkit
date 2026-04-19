from core import runner, target
import argparse

def run(args):
    # Pass arguments to module
    result = runner.run_module_by_name("ad.changepass", args.extra)

    if result and result.get("success"):
        user, password = result['user'], result['pass']

        # Update DB quietly (No printing the whole table)
        target.target_add_cred(argparse.Namespace(
            user=user, password=password, hash=None, aes=None, ccache=None
        ))