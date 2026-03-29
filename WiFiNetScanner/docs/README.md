# Technical and user documentation
# WiFiNetScanner Documentation

This directory contains all technical and user documentation for WiFiNetScanner.

---

## Contents

- **1. Introduction & Overview**
    - Project vision, mission, and key features
    - How WiFiNetScanner differs from other tools

- **2. Architecture**
    - High-level architecture diagrams (core, modules, data flow)
    - Subsystem design (core, packets, interfaces, modules, utils, config, logging)

- **3. Installation**
    - System requirements
    - Installation and upgrade procedures
    - Virtual environment recommendations

- **4. Configuration**
    - Full description of all config parameters (see `config/default_config.yaml`)
    - Best practices for adapting to custom environments
    - Environment variable overrides

- **5. Usage**
    - CLI quickstart and advanced commands
    - Usage scenarios (e.g. basic WiFi scan, stealth scan, enterprise logging)
    - Sample outputs and troubleshooting

- **6. API Reference**
    - Auto-generated (Sphinx/reStructuredText) docs for all classes and modules
    - Inline code samples and best practices

- **7. Extending & Contributing**
    - How to add new core modules, plugins, or C++ extensions
    - Code style and review process
    - Test and CI/CD guidelines

- **8. Security Guidelines**
    - Threat modeling
    - Secure development practices
    - Responsible disclosure policy

- **9. Roadmap**
    - Feature plan, milestones, and long-term vision

---

## Building the Documentation

WiFiNetScanner uses [Sphinx](https://www.sphinx-doc.org/) for API and technical documentation.

To build the HTML documentation locally:

```bash
cd docs/
pip install -r requirements.txt
make html

Contributing to Documentation
All new features or modules must be documented here and with inline docstrings.

For API changes, update reStructuredText (.rst) files accordingly.

Follow professional writing standards: clarity, conciseness, and technical precision.

