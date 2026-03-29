# Security Policy

## Overview

This document defines the security policy for BackDoors_1.1, including how to report vulnerabilities in the framework itself and the scope of responsible use.

---

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.1.x   | Yes       |
| < 1.0   | No        |

---

## Reporting a Vulnerability

If you discover a security vulnerability in this framework (e.g., a flaw in the AES implementation, an unintended privilege escalation in the server, or a logic error in a module), please report it responsibly.

### How to Report

1. **Do NOT open a public GitHub issue** for security vulnerabilities. Public disclosure before a fix is available puts users at risk.
2. Send your report to: **security@example.com** (replace with actual contact)
3. Include in your report:
   - A clear description of the vulnerability
   - The component affected (core, modules, server, client)
   - Steps to reproduce
   - Your assessment of severity (Critical / High / Medium / Low)
   - Any proof-of-concept code (if applicable)
4. Encrypt sensitive reports using PGP if available.

### Response Timeline

| Action | Timeframe |
|--------|-----------|
| Acknowledgment of receipt | 48 hours |
| Initial assessment | 5 business days |
| Status update | 10 business days |
| Fix and coordinated disclosure | 30–90 days depending on severity |

---

## Scope

### In Scope

Vulnerabilities in the framework code itself:

- Cryptographic weaknesses in `core/aes_crypto.py` or `core/comms.py`
- Authentication bypass in the C2 server
- Memory safety issues in any module
- Privilege escalation vulnerabilities
- Insecure default configurations
- Dependency vulnerabilities in `requirements.txt`

### Out of Scope

- Reports about the tool's intended offensive capabilities (these are features, not bugs)
- Vulnerabilities in systems targeted by the tool (that is the tool's purpose — report those to the respective system owners)
- Social engineering attacks against contributors
- Denial-of-service attacks against the project infrastructure
- Issues in outdated, unsupported versions

---

## Responsible Disclosure Guidelines

We follow coordinated vulnerability disclosure:

1. Reporter submits vulnerability privately.
2. Maintainer acknowledges and begins investigation.
3. Fix is developed and tested.
4. Reporter is given advance notice of the fix release date.
5. Fix is released.
6. Reporter may publish their findings 30 days after the fix is released.

We will credit reporters in the release notes (unless they prefer anonymity).

---

## Security Best Practices for Users

- **Change the default AES key** in `core/config.py` before any use.
- **Run the server on a VPN or private network** — never expose the C2 port to the public internet.
- **Use only in authorized environments** — see [ETHICAL_USE.md](ETHICAL_USE.md).
- **Rotate keys between engagements** — reusing keys across different authorized tests is a security risk.
- **Delete compiled implants after each engagement** — do not keep live implants in storage.

---

## Legal Notice

Use of this tool against systems without explicit written authorization is illegal. The maintainers assume no liability for misuse. See [ETHICAL_USE.md](ETHICAL_USE.md) for the full legal framework.
