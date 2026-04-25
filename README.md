# ctfkit
ctfkit is a modular CLI for pentesting that removes the need to constantly retype commands, credentials, and target details. It uses stored context (targets, creds, URLs) to automatically build and run commands. Playbooks guide what to test, and modules handle the repetitive execution.

Key features:

- target management
- credential tracking
- modular execution
- shell generation
- structured playbooks (methodology engine)

---


## Core Concept
ctfkit is built around three layers:

### Targets
Store all context:

- IP, domain, URLs
- credentials
- notes

### Modules
Small, reusable actions:


```bash
ctf smb.enum
ctf nmap.scan
ctf shell.generate
```

### Playbooks 
Structured attack workflows:

```bash
ctf play web.auth.password
```

---

## Features

- Target & profile system
- Credential management (active identity tracking)
- URL management (multi-target web workflows)
- Modular execution engine
- Alias-based CLI (fast commands)
- Shell generation system (reverse shells, webshells)
- Artifacts system (auto-save outputs)
- Playbook system (checklists + commands + optional execution)
- Chain support (multi-step automation)


---

## Usage

### Create target
```bash
ctf create box --ip 10.10.10.10 --url http://box.local
```

### Switch target

```bash
ctf target use box
```

### URLs

```bash
ctf add-url http://admin.box.local
ctf set-url 1
```

### Credentials

```bash
ctf add-cred user 'password'
ctf cred
ctf set-cred 0
```

### Target info
```bash
ctf info
```

### Who am I
```bash
ctf whoami
```
### Run modules 

```bash
ctf smb.connect 'Department'
ctf nmap.scan
ctf win.upload sharphound.exe
ctf ad.dcsync
ctf shell php
```

### Playbooks

```bash
ctf play web.auth.password
ctf play web.auth.mfa
ctf play web.auth.other
```
Inside playbooks you can:

- navigate steps
- view payloads/commands
- mark steps complete
- jump between steps
- execute modules (optional)

---

## Example Workflow
### Manual
```bash
ctf target create lab --ip 10.10.10.10 --domain domain.local
ctf target add-cred robert 'password123!'

ctf :ad.kerberoast
ctf :crack.hash kerberoast_hashes.txt
ctf :parse.hash cracked.txt
```

### Automatic (chain)
```bash
ctf target create lab --ip 10.10.10.10 --domain domain.local
ctf target add-cred robert 'password123!'

ctf ad.kerberoast
```

---
## Project Structure
```
core/
  target.py        # profiles, creds, urls
  runner.py        # module execution
  playbook.py      # playbook engine
  aliases.py       # CLI shortcuts
  attacker.py      # lhost resolution
  chain.py         # chain execution
  

modules/
  smb/
  nmap/
  shell/
  ad/
  win/
  web/
  ...

playbooks/
  web/
    auth/
      password.yaml
      mfa.yaml
      other.yaml

artifacts/         # output storage
profiles/          # targets
```

---

## Status

Active development.

Current focus:

- Web exploitation workflows 
- Playbook system expansion
- Better module/playbook integration

