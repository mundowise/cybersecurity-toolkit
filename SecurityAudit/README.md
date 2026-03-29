# SecurityAudit

Lightweight host-based intrusion detection tool. Helps users determine if their system has been compromised by checking for suspicious network connections, unknown processes, and unexpected open ports.

## When to Use This

- You suspect your computer may be infected or backdoored
- You want to verify your system is clean after a security incident
- You need a quick baseline check of your system's network activity
- You want to monitor what processes are running and what ports are open

## What It Checks

| Check | What It Does |
|-------|-------------|
| **Network Connections** | Lists all active ESTABLISHED connections — shows what your machine is talking to right now |
| **Running Processes** | Lists every process with PID, name, and user — helps spot unknown or suspicious processes |
| **Open Ports** | Scans local ports 1-1024 — reveals services listening that shouldn't be |

## Installation

```bash
pip install psutil
```

## Usage

```bash
python main.py
```

### Output Example

```
Initiating security audit...

--- Active Network Connections ---
  Proto: TCP  Local: 192.168.1.5:52341  Remote: 142.250.80.46:443  Status: ESTABLISHED  PID: 1234

--- Running Processes ---
  PID: 1     Name: systemd       User: root
  PID: 1234  Name: firefox        User: orlando

--- Scanning Open Ports on 127.0.0.1 ---
  Port 22: Open
  Port 80: Open
  Port 443: Open

Basic security audit completed.
```

## What to Look For

**Suspicious network connections:**
- Connections to unknown IPs, especially on non-standard ports
- Connections to .onion addresses or Tor exit nodes
- Outbound traffic on ports you don't recognize

**Suspicious processes:**
- Processes with random or obfuscated names
- Processes running as root that shouldn't be
- Multiple instances of the same process
- Processes you don't recognize

**Unexpected open ports:**
- Ports open that you didn't configure
- High ports (above 1024) listening without explanation
- Common backdoor ports: 4444, 5555, 6666, 8080, 9999

## Limitations

This is a basic first-pass check, not a replacement for professional forensic analysis. It will not detect:
- Rootkits that hide processes from the OS
- Fileless malware running in memory only
- Backdoors that only activate on a schedule
- Compromised system libraries

For thorough analysis, use dedicated tools like rkhunter, chkrootkit, or engage a security professional.

## Requirements

- Python 3.8+
- psutil

## License

MIT License - Copyright (c) 2025 Orlando Fernandez

## Author

**Orlando Fernandez**
Founder, XPlus Technologies LLC
