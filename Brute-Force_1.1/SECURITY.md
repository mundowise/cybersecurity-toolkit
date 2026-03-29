# Security Policy

## Overview

This document defines the security policy for Brute-Force_1.1, including how to report vulnerabilities in the framework itself.

---

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.1.x   | Yes       |
| < 1.0   | No        |

---

## Reporting a Vulnerability

If you discover a security vulnerability in this framework (e.g., a flaw in the blacklist detection logic, a bypass of safety controls, or an unintended RCE in the GUI), please report it responsibly.

### How to Report

1. **Do NOT open a public GitHub issue** for security vulnerabilities.
2. Send your report to: **security@example.com** (replace with actual contact)
3. Include in your report:
   - Description of the vulnerability
   - Component affected (GUI, a specific module, core)
   - Steps to reproduce
   - Severity assessment (Critical / High / Medium / Low)
   - Proof-of-concept code if available
4. Use PGP encryption for sensitive reports if available.

### Response Timeline

| Action | Timeframe |
|--------|-----------|
| Acknowledgment | 48 hours |
| Initial assessment | 5 business days |
| Status update | 10 business days |
| Fix and disclosure | 30–90 days |

---

## Scope

### In Scope

- Logic errors in the blacklist/lockout detection system
- Authentication issues in module connections
- Dependency vulnerabilities in `requirements.txt`
- Insecure defaults in `src/core/config.py`
- Data injection in wordlist parsing
- GUI privilege escalation issues

### Out of Scope

- The intended functionality of authentication testing modules
- Issues in third-party tools (hashcat, john, aircrack-ng) — report those to their respective projects
- Vulnerabilities in target systems discovered during authorized testing — report those to the system owners
- Issues in unsupported versions

---

## Responsible Disclosure Guidelines

1. Report the vulnerability privately.
2. Allow 30 days for a fix before public disclosure.
3. Do not test vulnerabilities against production systems.
4. Reporters will be credited in release notes unless they prefer anonymity.

---

## Security Best Practices for Users

- **Always run in isolated lab environments** for any testing.
- **Use configurable delays** — aggressive settings can cause denial-of-service on target systems, which may fall outside the authorized scope.
- **Log all activity** — the built-in logger provides an audit trail.
- **Review scope** before starting any test — test only hosts explicitly in scope.
- **Store wordlists securely** — wordlists can contain sensitive information about organizational password patterns.

---

## Legal Notice

Unauthorized use of this tool is illegal. See [ETHICAL_USE.md](ETHICAL_USE.md) for the full legal framework and authorization requirements.
