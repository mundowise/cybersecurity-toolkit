# EncriptadoX — Cross-Platform Encryption and Steganography Tool

A desktop application for secure message encryption and steganography. Built with PyQt6, it provides AES encryption, secure password generation, and steganographic concealment of messages within innocent-looking cover texts.

## Features

- **AES Encryption** — Encrypt and decrypt messages using industry-standard AES symmetric encryption via the `cryptography` library (Fernet/AES-128-CBC)
- **Secure Password Generation** — Generate cryptographically random passwords with configurable length and character sets
- **Steganography** — Hide encrypted messages inside natural-language cover texts to conceal the existence of communication
- **Multi-language Interface** — Full UI support for English, Spanish, and French (locales via JSON translation files)
- **Dark and Light Themes** — Toggle between dark and light modes at runtime
- **Cross-platform** — Runs on Windows, macOS, and Linux via PyQt6

## Screenshots

| Dark Theme | Light Theme |
|------------|-------------|
| Encryption panel with password field and output area | Same layout in light mode |

The main window includes:
- Message input field (up to 1000 characters)
- Language selector (EN / ES / FR)
- Theme toggle button
- Encrypt / Decrypt controls
- Password generator panel
- Steganography output with cover text selection

## Requirements

- Python 3.10 or higher
- PyQt6
- cryptography

## Installation

```bash
# Clone the repository
git clone https://github.com/your-org/EncriptadoX.git
cd EncriptadoX

# Install dependencies
pip install PyQt6 cryptography

# Run
python main.py
```

No build step required. All dependencies are pure Python or have pre-built wheels for Windows, macOS, and Linux.

## Usage

### Encrypt a Message

1. Type your message in the input field (max 1000 characters)
2. Enter or generate a password
3. Click **Encrypt** — the encrypted output appears in the output area
4. Optionally click **Hide in Text** to embed the ciphertext in a cover text for steganography

### Decrypt a Message

1. Paste the encrypted string (or steganographic cover text) into the input field
2. Enter the decryption password
3. Click **Decrypt** — the plaintext appears in the output area

### Generate a Password

1. Navigate to the Password Generator panel
2. Set desired length and character options
3. Click **Generate** — the password is displayed and can be copied

### Steganography

Cover texts are loaded from the `cover_texts/` directory (one file per language). The tool embeds the encrypted payload into a naturally-worded paragraph that can be shared without arousing suspicion.

## Project Structure

```
EncriptadoX/
├── main.py           Entry point
├── gui.py            PyQt6 main window and UI logic
├── crypto.py         AES encryption, password generation, key management
├── stego.py          Steganography: hide and extract messages from cover texts
├── locales/          Translation files (en.json, es.json, fr.json)
├── cover_texts/      Cover text templates per language
├── tests/            Unit tests
└── logo.png          Application logo
```

## Running Tests

```bash
pytest tests/
```

## Security Notes

- Passwords are never stored in plaintext; keys are derived via a KDF
- The application logs debug information to `debug.log` — review before sharing log files
- See [SECURITY.md](SECURITY.md) to report vulnerabilities

## Ethical Use

This tool is intended for legitimate privacy protection. See [ETHICAL_USE.md](ETHICAL_USE.md) for the full policy.

## License

MIT License — see [LICENSE](LICENSE) for details.

Copyright 2025 Orlando Fernandez
