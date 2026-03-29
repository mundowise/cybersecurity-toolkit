# Contributing to BackDoors_1.1

Thank you for your interest in contributing. This project exists to advance legitimate cybersecurity research and red team tooling. Contributions are welcome provided they meet the standards below.

---

## Before You Contribute

By submitting a contribution, you confirm that:

1. You have read and agree to the [ETHICAL_USE.md](ETHICAL_USE.md) policy.
2. Your contribution is intended solely for authorized security testing and defensive research.
3. You are not introducing capabilities designed to harm individuals or systems without consent.
4. You have the legal right to contribute the code you submit (no proprietary code, no license conflicts).

---

## Workflow

### Fork and Branch

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/your-username/BackDoors_1.1.git
cd BackDoors_1.1

# Create a feature branch
git checkout -b feature/your-feature-name

# Or a fix branch
git checkout -b fix/description-of-fix

# Or a docs branch
git checkout -b docs/what-you-are-documenting
```

### Make Your Changes

- Keep changes focused — one feature or fix per pull request.
- Write clear commit messages: `feat: add SOCKS5 proxy support in comms` not `update stuff`.
- Update `requirements.txt` if you add a new dependency.
- Update the relevant section of `README.md` if your change adds or modifies a feature.

### Run the Tests

```bash
pytest tests/ -v
```

All existing tests must pass before submitting. If you add a new module, add tests for it in `tests/`.

### Open a Pull Request

1. Push your branch to your fork.
2. Open a pull request against the `main` branch of the upstream repository.
3. Fill in the PR description:
   - What does this change do?
   - Why is it needed?
   - What testing was done?
   - Does it introduce any new dependencies?

---

## Code Style

- Follow **PEP 8** for all Python code.
- Use type hints for all function signatures.
- Write docstrings for all public functions and classes.
- Keep functions small and single-purpose.
- Do not leave debug `print()` statements — use the `logger` module.

### Example

```python
from core.logger import Logger

log = Logger(__name__)

def encrypt_payload(data: bytes, key: bytes) -> bytes:
    """
    Encrypt a payload using AES-256-CFB.

    Args:
        data: Raw bytes to encrypt.
        key: 32-byte AES key.

    Returns:
        IV-prepended ciphertext as bytes.
    """
    ...
```

---

## Test Requirements

- Every new module in `modules/` must have a corresponding test file in `tests/`.
- Tests must cover: normal operation, edge cases, and error handling.
- Use `pytest` and `pytest-mock` for mocking external dependencies.
- Minimum test coverage for new code: 80%.

```bash
# Run with coverage
pytest tests/ --cov=. --cov-report=term-missing
```

---

## Adding a New Module

1. Create your module in `modules/your_module.py`.
2. Implement a `run(cmd, *args)` interface to match the existing module API.
3. Register the module in `modules/__init__.py`.
4. Add tests in `tests/test_your_module.py`.
5. Document the module in `README.md` under the Features section.

---

## Security Contributions

If you discover a vulnerability in the framework itself, do NOT submit it as a pull request or public issue. Follow the [SECURITY.md](SECURITY.md) responsible disclosure process.

---

## Code of Conduct

- Be professional and respectful in all interactions.
- Contributions that introduce malicious capabilities targeting unauthorized systems will be rejected and reported.
- This project is for the defensive security community. Contributions that undermine this mission are not welcome.
