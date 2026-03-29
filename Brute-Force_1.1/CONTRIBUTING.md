# Contributing to Brute-Force_1.1

Contributions are welcome from the security research community. All contributions must serve the framework's purpose: enabling authorized authentication security testing.

---

## Legal Acknowledgment

By submitting a contribution, you confirm that:

1. You have read and agree to the [ETHICAL_USE.md](ETHICAL_USE.md) policy.
2. Your contribution is intended for authorized security testing only.
3. You are not introducing capabilities that facilitate unauthorized access.
4. You have the legal right to submit the code (no third-party IP, no license conflicts).

---

## Workflow

### Fork and Branch

```bash
git clone https://github.com/your-username/Brute-Force_1.1.git
cd Brute-Force_1.1
git checkout -b feature/your-feature-name
# or
git checkout -b fix/description
# or
git checkout -b docs/what-you-document
```

### Make Changes

- Keep pull requests focused — one feature or fix per PR.
- Write clear commit messages: `feat: add LDAP authentication module` not `added stuff`.
- Update `requirements.txt` for new dependencies.
- Update the protocol table in `README.md` if you add a new protocol module.

### Run Tests

```bash
pytest tests/ -v
```

All existing tests must pass. New modules require new tests.

---

## Code Style

- Follow **PEP 8** for all Python code.
- Use type hints in all function signatures.
- Write docstrings for all public functions and classes.
- Use the project's `logger` module — no raw `print()` statements.

### Adding a New Protocol Module

Each protocol module in `src/modules/` must follow this interface:

```python
from src.core.logger import Logger

log = Logger(__name__)

def test_credentials(host: str, port: int, username: str, password: str, timeout: int = 5) -> bool:
    """
    Test a single username/password combination against the target.

    Args:
        host: Target hostname or IP address.
        port: Target port number.
        username: Username to test.
        password: Password to test.
        timeout: Connection timeout in seconds.

    Returns:
        True if authentication succeeded, False otherwise.
    """
    ...
```

Register your module in `src/modules/__init__.py` and add it to the GUI dropdown in `src/gui/main_gui.py`.

---

## Test Requirements

- Every new module in `src/modules/` requires tests in `tests/`.
- Use `pytest-mock` to mock network connections — tests must not make real network calls.
- Test: successful authentication, failed authentication, connection timeout, and blacklist detection.

```bash
# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing
```

---

## Opening a Pull Request

1. Push your branch to your fork.
2. Open a PR against the `main` branch.
3. Describe:
   - What the change does.
   - Why it is needed.
   - What testing was performed.
   - Any new dependencies added.

---

## Code of Conduct

- Be professional in all interactions.
- This project serves the defensive security community.
- Contributions designed to facilitate unauthorized access will be rejected.
