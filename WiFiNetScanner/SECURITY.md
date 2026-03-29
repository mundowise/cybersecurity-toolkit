# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly.

**Do NOT open a public issue.** Public disclosure before a fix is available puts all users at risk.

Instead, email: security@xplustechnologies.com

### What to Include

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact and attack scenarios
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

We only maintain the latest release. If you are running an older version, please upgrade before reporting a vulnerability.

## Security Considerations for Users

WiFiNetScanner requires elevated privileges (root/admin) on most operating systems to perform raw socket operations and interface management. Run it only in controlled environments and be aware of the following:

- Elevated privileges increase the attack surface if the tool itself has a vulnerability
- Scan data may contain sensitive network information — store and transmit it securely
- Never run untrusted scan configurations from third parties
