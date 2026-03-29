# Contributing

Contributions are welcome. Please read these guidelines before submitting.

## Project Structure

SecureMessenger is a full-stack project with multiple clients:

```
SecureMessenger/
├── backend/        Flask backend (Python)
├── frontend/       Flutter multi-platform client (iOS, Android, Web, Desktop)
└── docs/           Architecture and protocol documentation
```

Make sure you are contributing to the right component and follow the conventions for that stack.

## How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Make your changes
4. Run the relevant test suite (see below)
5. Commit with a clear, descriptive message
6. Push your branch and open a Pull Request

## Running Tests

**Backend (Python/Flask):**
```bash
cd backend
pip install -r requirements.txt
pytest tests/
```

**Frontend (Flutter):**
```bash
cd frontend
flutter pub get
flutter test
```

## Code Standards

### Backend (Python)

- Follow PEP 8
- Add docstrings for all public functions and classes
- Add comments for cryptographic or security-sensitive logic
- Include unit tests for new endpoints or business logic changes

### Frontend (Flutter/Dart)

- Follow the official [Dart style guide](https://dart.dev/guides/language/effective-dart/style)
- Use `flutter analyze` to check for issues before committing
- Keep UI logic and business logic separated
- Test new widgets with widget tests

## Types of Contributions

### Bug Reports

Open an issue with:
- A clear title describing the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python/Flutter version, deployment method)

### Feature Requests

Open an issue describing:
- The use case the feature addresses
- Proposed behavior
- Any alternatives you considered

### Pull Requests

- Keep changes focused — one PR per logical change
- Reference any related issue in the PR description (`Closes #123`)
- Ensure all tests pass before requesting review
- Include a brief description of what was changed and why

## Security Contributions

If your contribution touches encryption, key management, authentication, or message handling:

- Justify cryptographic design decisions with references to current best practices
- Do not reduce security parameters (key lengths, iteration counts, authentication requirements)
- Tag your PR with the `security` label so it receives additional review

If you discover a security vulnerability rather than a code improvement, follow the responsible disclosure process in [SECURITY.md](SECURITY.md) instead of opening a PR.

## Legal

By contributing, you agree that your contributions will be licensed under the MIT License (see LICENSE).

## Ethical Requirement

All contributions must comply with the project's Ethical Use Policy (ETHICAL_USE.md). Do not add features designed to weaken user privacy, circumvent end-to-end encryption, introduce backdoors, or facilitate surveillance of users without their knowledge and consent.
