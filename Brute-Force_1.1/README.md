# Brute-Force_1.1 — Multi-Protocol Authentication Testing Framework

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows-lightgrey.svg)
![Protocols](https://img.shields.io/badge/protocols-22%2B-orange.svg)

> A modular, multi-threaded authentication strength auditing framework supporting 22+ protocols and services. Built for authorized security professionals.

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

Brute-Force_1.1 is a professional authentication auditing framework designed for penetration testers and security teams conducting authorized assessments. It enables systematic testing of password policies across a wide range of protocols and services through a modern ttkbootstrap GUI.

This tool helps organizations answer the question: **"Are our passwords strong enough to resist a real attack?"** — in a controlled, authorized test environment.

---

## Features

### Protocol Support (22+ protocols)

| Category | Protocols |
|----------|-----------|
| Remote Access | SSH, Telnet, WinRM, VNC |
| Database | MySQL, PostgreSQL, MSSQL, MongoDB, Redis |
| Mail | SMTP, IMAP, POP3 |
| File Sharing | FTP, SMB |
| Web | HTTP Basic Auth, HTTP POST form |
| Archive | ZIP, RAR |
| Network | WiFi (WPA/WPA2) |
| Discovery | Nmap integration |

### Core Capabilities

- Multi-threaded engine with configurable thread count
- Full GUI built with ttkbootstrap (dark theme)
- Real-time progress bars and live statistics
- Dictionary management (custom wordlists, username/password files)
- Pause, resume, and stop controls
- Blacklist/lockout detection with automatic backoff
- CAPTCHA detection handling
- Random combination generation mode
- Hash cracking module (hashcat + john integration)
- CSV and PDF export of results
- Real-time graphs for progress visualization

---

## Architecture

```
Brute-Force_1.1/
├── main.py                     # Application entry point (ttkbootstrap GUI)
├── src/
│   ├── gui/
│   │   └── main_gui.py         # Main GUI class (FuerzaBrutaGUI)
│   ├── core/
│   │   ├── config.py           # Global configuration and defaults
│   │   ├── blacklist.py        # Lockout and blacklist detection
│   │   ├── logger.py           # Logging subsystem
│   │   ├── password_ai.py      # Password mutation and generation
│   │   └── utils.py            # Shared utilities
│   ├── modules/                # Protocol-specific attack modules
│   │   ├── ftp.py
│   │   ├── ssh.py
│   │   ├── mysql.py
│   │   ├── postgresql.py
│   │   ├── mssql.py
│   │   ├── smtp.py
│   │   ├── imap.py
│   │   ├── pop3.py
│   │   ├── smb.py
│   │   ├── vnc.py
│   │   ├── redis.py
│   │   ├── mongodb.py
│   │   ├── telnet.py
│   │   ├── winrm.py
│   │   ├── http_post.py
│   │   ├── http_basic.py
│   │   ├── zip.py
│   │   ├── rar.py
│   │   ├── wifi_crack.py
│   │   ├── nmap.py
│   │   ├── hash_crack.py       # Hash cracking (hashcat/john)
│   │   └── password_ai.py      # AI-assisted password mutations
│   └── brute_manager.py        # Attack orchestration and thread management
├── data/                       # Wordlists and dictionaries
├── tools/                      # External tool integration
├── tests/                      # pytest test suite
├── setup.sh                    # Linux installer
├── requirements.txt
└── MANUAL.txt                  # Detailed usage guide
```

---

## Requirements

- Python 3.8 or higher
- Linux (recommended) or Windows
- For hash cracking: `hashcat` and/or `john` installed on the system
- For WiFi testing: `aircrack-ng` installed on the system

---

## Installation

```bash
# Install system dependencies (Debian/Ubuntu/Kali)
sudo apt install -y hashcat john aircrack-ng

# Clone the repository
git clone https://github.com/your-username/Brute-Force_1.1.git
cd Brute-Force_1.1

# Run the installer (installs Python dependencies)
bash setup.sh
```

### Manual Installation

```bash
pip install -r requirements.txt
```

---

## Usage

### Launch the GUI

```bash
python3 main.py
```

The ttkbootstrap GUI opens with the darkly theme. From the GUI:

1. Select the target protocol from the dropdown.
2. Enter the target host and port.
3. Load a username list and password wordlist.
4. Configure thread count and delay settings.
5. Click **Start** to begin the audit.
6. Monitor real-time progress in the stats panel.
7. Export results to CSV or PDF when complete.

### Hash Cracking Module

The hash cracking module supports:
- Auto-detection of hash type
- hashcat integration (GPU acceleration)
- john the ripper integration
- Export of cracked hashes to CSV/PDF

---

## Configuration

Edit `src/core/config.py` to set defaults:

```python
DEFAULT_THREADS = 10        # Concurrent threads
DEFAULT_TIMEOUT = 5         # Connection timeout (seconds)
DEFAULT_DELAY = 0.5         # Delay between attempts (seconds)
MAX_BLACKLIST_HITS = 3      # Lockout detection threshold
```

---

## Safety Features

This framework includes several features designed for responsible use:

- **Lockout detection**: Automatically detects authentication blacklisting and pauses.
- **Configurable delays**: Prevents aggressive testing that could disrupt services.
- **Audit logging**: All attempts are logged for post-engagement review.
- **Scope limitation**: Test only the targets you configure — no auto-discovery of additional targets.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Ethical Use

See [ETHICAL_USE.md](ETHICAL_USE.md) for the full ethical use policy, authorization requirements, and applicable laws.

---

## Security Policy

See [SECURITY.md](SECURITY.md) for vulnerability reporting.

---

## License

MIT License — see [LICENSE](LICENSE) for full text.

Copyright (c) 2025 Orlando Fernandez
