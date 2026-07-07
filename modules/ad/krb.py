PROVIDES = []
REQUIRES = ["domain"]

def run(data, cred, args):
    from pathlib import Path
    import subprocess

    from core.target import load_current_profile

    G, C, B, Y, W, R = (
        '\033[92m',
        '\033[96m',
        '\033[94m',
        '\033[93m',
        '\033[0m',
        '\033[91m'
    )
    BOLD = '\033[1m'

    data, _ = load_current_profile()

    domain = data.get("domain")
    hostname = data.get("hostname")

    if not domain:
        print(f"{R}[!] No domain found in current profile{W}")
        return

    if not hostname:
        print(f"{R}[!] No hostname found in current profile{W}")
        return

    realm = domain.upper()
    dc_fqdn = f"{hostname.lower()}.{domain}"

    krb_conf = f"""[libdefaults]
    default_realm = {realm}
    dns_lookup_realm = false
    dns_lookup_kdc = false
    rdns = false
    forwardable = true

[realms]
    {realm} = {{
        kdc = {dc_fqdn}
        admin_server = {dc_fqdn}
    }}

[domain_realm]
    .{domain} = {realm}
    {domain} = {realm}
"""

    print(f"\n{B}[{W}{G}*{W}{B}]{W} {BOLD}KERBEROS CONFIGURATION{W}")

    temp_file = Path("/tmp/ctf_krb5.conf")
    temp_file.write_text(krb_conf)

    backup_cmd = (
        "if [ ! -f /etc/krb5.conf.ctf.bak ]; then "
        "cp /etc/krb5.conf /etc/krb5.conf.ctf.bak; "
        "fi"
    )

    subprocess.run(
        f"sudo sh -c '{backup_cmd}'",
        shell=True
    )

    subprocess.run(
        f"sudo cp {temp_file} /etc/krb5.conf",
        shell=True
    )

    print(
        f"{G}[+]{W} Realm: {C}{realm}{W}\n"
        f"{G}[+]{W} KDC:   {C}{dc_fqdn}{W}\n"
        f"{G}[+]{W} Installed new {C}/etc/krb5.conf{W}\n"
        f"{Y}[!]{W} Original backed up to "
        f"{C}/etc/krb5.conf.ctf.bak{W}"
    )

    print(
        f"\n{B}Next steps:{W}\n"
        f"  kdestroy\n"
        f"  getTGT.py {domain}/user:password\n"
        f"  export KRB5CCNAME=<ticket>.ccache\n"
        f"  kvno cifs/{dc_fqdn}\n"
    )
