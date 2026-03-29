# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly.

**Do NOT open a public issue.** A public disclosure before a fix is available could put users at risk.

Instead, email: security@xplustechnologies.com

### What to Include

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact (e.g., key recovery, plaintext leakage, privilege escalation)
- Suggested fix (if any)
- Your contact information for follow-up

### Response Timeline

| Stage | Timeline |
|-------|----------|
| Acknowledgment | Within 48 hours |
| Initial assessment | Within 5 business days |
| Fix timeline | Communicated after assessment; depends on severity |
| Public disclosure | Coordinated with the reporter after fix is released |

## Supported Versions

| Version | Supported |
|---------|-----------|
| Latest  | Yes       |
| Older   | No        |

## Cryptographic Scope

This project uses the Python `cryptography` library for all cryptographic operations. If a vulnerability is discovered in the underlying `cryptography` package (e.g., a CVE), update the dependency immediately:

```bash
pip install --upgrade cryptography
```

Security-relevant areas of this codebase:

- `crypto.py` — AES key derivation, encryption, decryption, and password generation
- `stego.py` — Steganographic embedding and extraction logic

If you find that the implementation in `crypto.py` weakens the underlying primitive (e.g., weak KDF parameters, predictable IV generation, insecure key storage), that constitutes a vulnerability and should be reported via the process above.

## Out of Scope

- Issues in third-party dependencies (report directly to the upstream maintainer)
- UI cosmetic bugs
- Feature requests
