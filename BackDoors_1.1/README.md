# BackDoors_1.1 — Modular Remote Access Testing Framework

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows-lightgrey.svg)
![Status](https://img.shields.io/badge/status-active-green.svg)

> A modular, AES-encrypted Command & Control (C2) framework for authorized penetration testing and red team operations.

---

## Legal Disclaimer

> **READ BEFORE USE**

This tool is provided for **authorized security testing and educational purposes ONLY**.

Unauthorized access to computer systems is illegal under:
- **United States**: Computer Fraud and Abuse Act (CFAA), 18 U.S.C. § 1030
- **European Union**: Directive 2013/40/EU on attacks against information systems
- **United Kingdom**: Computer Misuse Act 1990
- **Most jurisdictions worldwide** have similar laws

**You MUST have explicit written authorization** from the system owner before using this tool.
The authors assume NO responsibility for misuse or damage caused by this software.
By using this tool, you agree to use it only on systems you own or have written permission to test.

---

## Overview

BackDoors_1.1 is a professional-grade remote access testing framework built for authorized penetration testers and red team operators. It provides an encrypted C2 channel with a modular payload architecture, enabling security professionals to simulate real-world intrusion scenarios in controlled, authorized environments.

**This is NOT intended for unauthorized use. Every capability in this framework is designed to replicate threats that defenders need to understand and detect.**

---

## Features

- AES-256 encrypted reverse connection channel (CFB mode)
- Multi-victim C2 server with both CLI and GUI (Tkinter) interfaces
- Modular attack simulation modules:
  - Keylogger (cross-platform, pynput-based)
  - Screenshot capture
  - Credential harvesting simulation
  - Browser cookie extraction
  - File exfiltration
  - Persistence mechanisms (multi-level)
  - USB and LAN propagation simulation (SMB/SSH)
  - Anti-forensic and camouflage modules
  - Secure kill switch
- Anti-VM detection for lab environment validation
- Plugin architecture for custom module extensions
- Cross-platform support (Windows and Linux)
- PyInstaller-ready client build pipeline
- PDF report export for engagement documentation
- Automated test suite (pytest)

---

## Architecture

```
BackDoors_1.1/
├── core/                   # Framework nucleus
│   ├── aes_crypto.py       # AES-256-CFB encryption/decryption
│   ├── comms.py            # Encrypted socket communications
│   ├── config.py           # C2 host/port configuration
│   ├── anti_vm.py          # VM detection
│   ├── logger.py           # Logging subsystem
│   └── utils.py            # Shared utilities
├── modules/                # Simulation modules
│   ├── keylogger.py        # Keystroke capture
│   ├── screengrab.py       # Screen capture
│   ├── credentials.py      # Credential harvesting
│   ├── cookies.py          # Browser cookie extraction
│   ├── exfiltrator.py      # File exfiltration
│   ├── persistence.py      # Persistence mechanisms
│   ├── propagator.py       # Network/USB propagation
│   ├── antiforensic.py     # Anti-forensic techniques
│   ├── camouflage.py       # Process camouflage
│   ├── watcher.py          # File system monitoring
│   ├── secure_kill.py      # Secure self-termination
│   └── file_protect.py     # File protection
├── plugins/                # Optional plugin extensions
├── cliente/                # Client implant (compile with PyInstaller)
│   └── main.py
├── server/                 # C2 server
│   ├── main.py             # CLI interface
│   ├── gui.py              # Tkinter GUI interface
│   └── export_report.py    # PDF report generator
├── tests/                  # pytest test suite
├── setup.sh                # Linux installer
└── setup.bat               # Windows installer
```

---

## Requirements

- Python 3.8 or higher
- Kali Linux (recommended) or any Linux distribution / Windows
- Root or Administrator privileges for some modules

---

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/BackDoors_1.1.git
cd BackDoors_1.1

# Install dependencies (Linux)
sudo bash setup.sh

# Install dependencies (Windows)
setup.bat

# Verify installation
pytest tests/
```

---

## Configuration

Edit `core/config.py` before deployment:

```python
C2_HOST = "0.0.0.0"    # C2 listener IP
C2_PORT = 4444          # C2 listener port
AES_KEY = b"..."        # 32-byte AES key (change this)
```

---

## Usage

### Start the C2 Server (CLI)

```bash
python3 server/main.py
```

C2 console commands:
```
C2 > list               # List connected targets
C2 > connect <id>       # Interact with target by ID
C2 > exit               # Shut down the C2 server
```

### Start the C2 Server (GUI)

```bash
python3 server/gui.py
```

### Build the Client Implant

```bash
pyinstaller \
  --onefile \
  --noconsole \
  --add-data "core:core" \
  --add-data "modules:modules" \
  cliente/main.py
```

The compiled binary is output to `dist/main` (Linux) or `dist/main.exe` (Windows).

### Generate a Test Report

```bash
python3 server/export_report.py
```

---

## Security Design

| Component | Implementation |
|-----------|----------------|
| Transport encryption | AES-256-CFB with random IV per message |
| Key derivation | Static pre-shared key (configurable) |
| Anti-analysis | VM detection, process camouflage |
| Forensic resistance | Secure memory wiping, anti-forensic module |
| Communication | TCP reverse shell, encrypted payload |

---

## Development

```bash
# Run the test suite
pytest tests/ -v

# Run specific module tests
pytest tests/test_crypto.py -v
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

---

## Ethical Use

See [ETHICAL_USE.md](ETHICAL_USE.md) for the full ethical use policy, applicable laws, and authorization requirements.

---

## Security Policy

See [SECURITY.md](SECURITY.md) to report vulnerabilities or review the responsible disclosure policy.

---

## License

MIT License — see [LICENSE](LICENSE) for full text.

Copyright (c) 2025 Orlando Fernandez
