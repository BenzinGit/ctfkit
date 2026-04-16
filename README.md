# ctfkit
A modular CLI toolkit for managing targets, credentials, and automating CTF and Active Directory workflows.

---

## ⚠️ Warning

This tool stores credentials locally in JSON files.

Do NOT commit the following directories:
- `profiles/`
- `domains/`

Make sure they are included in your `.gitignore`.

---

## Features

- Target management (`create`, `use`, `show`)
- Credential handling (local + domain-aware)
- Modular execution system (`smb`, `nmap`, etc.)
- Alias-based CLI for fast workflows
- Active identity tracking (`whoami`)

---

## Usage

### Create target
```bash
ctf target create box --ip 10.2.10.10
```
### Add domain

```bash
ctf target add-domain --domain domain.htb
```

### Add credentials

```bash
ctf target ctf target add-cred user 'password'
```
### Show credentials
```bash
ctf target creds
ctf target creds --local
ctf target creds --domain
```
### Set active credential

```bash
ctf target set-cred 1
ctf target set-cred username
```

### Who am I
```bash
ctf whoami
```

### Run modules
```bash
ctf smb.list
ctf smb.connect sysvol
ctf nmap.scan
ctf nmap.fast
```
--- 

## Structure
```
core/
  target.py
  runner.py
  aliases.py

modules/
  smb/
  nmap/
  util/

profiles/   # ignored
domains/    # ignored
```
## Notes

This project is under active development and mainly intended for:

- CTF practice
- Learning pentesting workflows
- Building modular tooling


