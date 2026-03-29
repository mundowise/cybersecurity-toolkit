# Contributing

Contributions are welcome. Please read these guidelines before submitting.

## How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Make your changes
4. Run the test suite (`pytest tests/`)
5. Commit with a clear, descriptive message
6. Push your branch and open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/EncriptadoX.git
cd EncriptadoX

# Install dependencies
pip install PyQt6 cryptography pytest

# Run tests
pytest tests/

# Run the application
python main.py
```

## Code Standards

- Follow PEP 8 style guidelines
- Add docstrings for all public functions and classes
- Add comments for complex cryptographic or steganographic logic
- Include unit tests for new features or bug fixes
- Update the README if you add or change features

## Adding a Language

To add a new language to the interface:

1. Create `locales/{lang_code}.json` with all translation keys (copy `locales/en.json` as a template)
2. Add a corresponding cover text file in `cover_texts/`
3. Add the language code and name to `SUPPORTED_LANGUAGES` in `gui.py`
4. Test all UI elements at the new locale

## Cryptographic Contributions

Changes to `crypto.py` require extra scrutiny:

- Justify any change to key derivation parameters with references to current best practices
- Do not reduce key length, iteration counts, or entropy sources
- Add test vectors where possible
- Ping the maintainer for review before merging cryptographic changes

## Types of Contributions

### Bug Reports

Open an issue with:
- A clear title describing the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, PyQt6 version)

### Feature Requests

Open an issue describing:
- The use case the feature addresses
- Proposed behavior
- Any alternatives you considered

## Legal

By contributing, you agree that your contributions will be licensed under the MIT License (see LICENSE).

## Ethical Requirement

All contributions must comply with the project's Ethical Use Policy (ETHICAL_USE.md). Do not add features designed to bypass lawful processes, facilitate illegal activity, or weaken the privacy protections the tool provides to users.
