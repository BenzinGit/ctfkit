import subprocess
from pathlib import Path


def run(data, cred, args):
    """
    Extract key and certificate from PFX file

    Usage:
        ctf ad.pfxextract file.pfx
    """

    extra = getattr(args, "extra", []) or []

    if not extra:
        print("[-] Missing PFX file")
        return data

    pfx_file = Path(extra[0]).expanduser()

    if not pfx_file.exists():
        print(f"[-] File not found: {pfx_file}")
        return data

    # -------------------------
    # Output filenames
    # -------------------------
    base = pfx_file.stem

    key_file = pfx_file.with_name(f"{base}.key")
    crt_file = pfx_file.with_name(f"{base}.crt")

    # -------------------------
    # Extract private key
    # -------------------------
    key_cmd = [
        "openssl", "pkcs12",
        "-in", str(pfx_file),
        "-nocerts",
        "-out", str(key_file),
        "-nodes"   # no encryption on key (important for automation)
    ]

    print(f"[*] Extracting private key → {key_file.name}")

    try:
        subprocess.run(key_cmd, check=True)
    except subprocess.CalledProcessError:
        print("[-] Failed to extract private key")
        return data

    # -------------------------
    # Extract certificate
    # -------------------------
    crt_cmd = [
        "openssl", "pkcs12",
        "-in", str(pfx_file),
        "-clcerts",
        "-nokeys",
        "-out", str(crt_file)
    ]

    print(f"[*] Extracting certificate → {crt_file.name}")

    try:
        subprocess.run(crt_cmd, check=True)
    except subprocess.CalledProcessError:
        print("[-] Failed to extract certificate")
        return data

    print("\n[+] Extraction complete:")
    print(f"    Key: {key_file}")
    print(f"    CRT: {crt_file}")

    # Return artifact info (for chains later)
    return {
        "key": str(key_file),
        "crt": str(crt_file)
    }