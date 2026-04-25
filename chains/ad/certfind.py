def run(args):
    from core.runner import run_module_by_name
    from core.target import load_current_profile, save_profile
    from core.paths import get_chain_artifacts_dir
    import json

    data, path = load_current_profile()

    print("[*] Step 1: Running certipy find...")

    # -------------------------
    # Prepare artifacts dir
    # -------------------------
    artifacts = get_chain_artifacts_dir(data["name"], "certfind")

    for f in artifacts.glob("*_Certipy.json"):
        f.unlink()

    # -------------------------
    # Run module
    # -------------------------
    module_args = ["--artifacts-dir", str(artifacts)]
    run_module_by_name("ad.certfind", module_args, data)

    # -------------------------
    # Locate JSON
    # -------------------------
    json_files = sorted(artifacts.glob("*_Certipy.json"))

    if not json_files:
        print("[-] No certipy JSON found")
        return

    json_path = json_files[-1]
    print(f"[*] Step 2: Parsing {json_path.name}...")

    # -------------------------
    # Load JSON safely
    # -------------------------
    try:
        certipy_data = json.loads(json_path.read_text())
    except Exception as e:
        print(f"[-] Failed to parse JSON: {e}")
        return

    # -------------------------
    # Normalize structures
    # -------------------------
    def safe_dict(obj):
        return obj if isinstance(obj, dict) else {}

    cas = safe_dict(certipy_data.get("Certificate Authorities"))
    templates = safe_dict(certipy_data.get("Certificate Templates"))

    # -------------------------
    # Extract ADCS info
    # -------------------------
    adcs = {
        "ca": None,
        "ca_vulns": [],
        "templates": []
    }

    # -------------------------
    # Extract CA + vulns
    # -------------------------
    for ca in cas.values():
        adcs["ca"] = ca.get("CA Name")

        vulns = safe_dict(ca.get("[!] Vulnerabilities"))
        for vuln_name in vulns.keys():
            adcs["ca_vulns"].append(vuln_name)

        break  # only one CA usually

    # -------------------------
    # Extract template vulns
    # -------------------------
    for tpl in templates.values():
        name = tpl.get("Template Name")

        vulns = safe_dict(tpl.get("[!] Vulnerabilities"))

        for vuln_name in vulns.keys():
            adcs["templates"].append({
                "name": name,
                "vuln": vuln_name
            })

    # -------------------------
    # Store in profile
    # -------------------------
    data.setdefault("adcs", {})
    data["adcs"] = adcs
    save_profile(data, path)

    # -------------------------
    # Output
    # -------------------------
    print("\n[+] ADCS Results:")

    if adcs["ca"]:
        print(f"    CA: {adcs['ca']}")

    if adcs["ca_vulns"]:
        print(f"    CA Vulnerabilities:")
        for v in adcs["ca_vulns"]:
            print(f"      - {v}")

    if adcs["templates"]:
        print(f"    Template Vulnerabilities:")
        for t in adcs["templates"]:
            print(f"      - {t['name']} ({t['vuln']})")
    else:
        print("    No vulnerable templates found")