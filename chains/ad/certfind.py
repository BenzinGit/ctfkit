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

    # Clean old JSON files
    for f in artifacts.glob("*_Certipy.json"):
        f.unlink()

    # -------------------------
    # Run module
    # -------------------------
    module_args = ["--artifacts-dir", str(artifacts)]
    run_module_by_name("ad.certfind", module_args, data)

    # -------------------------
    # Find JSON file
    # -------------------------
    json_files = sorted(artifacts.glob("*_Certipy.json"))

    if not json_files:
        print("[-] No certipy JSON found")
        return

    json_path = json_files[-1]

    print(f"[*] Step 2: Parsing {json_path.name}...")

    # -------------------------
    # Load JSON
    # -------------------------
    try:
        certipy_data = json.loads(json_path.read_text())
    except Exception as e:
        print(f"[-] Failed to parse JSON: {e}")
        return

    # -------------------------
    # Extract ADCS data
    # -------------------------
    adcs = {
        "ca": None,
        "templates": []
    }

    # -------------------------
    # Extract CA
    # -------------------------
    cas = certipy_data.get("Certificate Authorities", {})

    for ca in cas.values():
        adcs["ca"] = ca.get("CA Name")
        break

    # -------------------------
    # Extract templates
    # -------------------------
    templates = certipy_data.get("Certificate Templates", {})

    for tpl in templates.values():
        name = tpl.get("Template Name")
        vulns = tpl.get("[!] Vulnerabilities", {})

        for vuln_name in vulns.keys():
            adcs["templates"].append({
                "name": name,
                "vuln": vuln_name
            })

    # -------------------------
    # Store in target
    # -------------------------
    data.setdefault("adcs", {})
    data["adcs"] = adcs

    save_profile(data, path)

    print("\n[+] ADCS info stored:")
    print(f"    CA: {adcs['ca']}")
    print(f"    Templates: {len(adcs['templates'])}")