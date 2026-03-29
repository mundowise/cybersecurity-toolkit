# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly.

**Do NOT open a public issue.** SecureMessenger handles encrypted communications. A public disclosure before a fix is in place could put users' privacy and safety at risk.

Instead, email: security@xplustechnologies.com

### What to Include

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact (e.g., message decryption, identity exposure, authentication bypass, server compromise)
- Affected component (backend, mobile client, web client, desktop client)
- Suggested fix (if any)
- Your contact information for follow-up

We do not require you to withhold disclosure indefinitely. We aim to fix critical issues quickly and will coordinate a public disclosure timeline with you.

### Response Timeline

| Stage | Timeline |
|-------|----------|
| Acknowledgment | Within 48 hours |
| Initial assessment | Within 5 business days |
| Fix timeline | Communicated after assessment; critical issues prioritized |
| Public disclosure | Coordinated with the reporter after fix is released |

## Supported Versions

| Version | Supported |
|---------|-----------|
| Latest  | Yes       |
| Older   | No        |

We only provide security fixes for the latest release. If you are running an older version, please upgrade before reporting a vulnerability.

## Scope

Security issues we are most interested in:

- Authentication and session management vulnerabilities
- End-to-end encryption weaknesses (key generation, key exchange, message encryption)
- Server-side injection vulnerabilities (SQLi, command injection, SSRF)
- Unauthorized access to messages or user data
- Client-side vulnerabilities that could expose message content
- Cryptographic implementation errors

## Out of Scope

- Denial of service attacks against your own self-hosted instance
- Issues requiring physical access to an already-compromised device
- Social engineering attacks
- Issues in third-party dependencies (report directly to the upstream maintainer, then notify us)

## Security Considerations for Operators

If you self-host SecureMessenger:

- Run the backend behind a reverse proxy with TLS (minimum TLS 1.2, recommend TLS 1.3)
- Keep dependencies updated — especially Flask, cryptographic libraries, and Flutter packages
- Restrict database access to the application process only
- Review file upload handling in `backend/uploads/` — ensure uploaded files are validated and isolated
- Enable security headers (HSTS, CSP, X-Frame-Options) in your reverse proxy configuration
