# Extension Modules (`modules/`)

This directory contains all extension modules for WiFiNetScanner, including:

- **C/C++ Native Extensions**: For high-performance packet processing, protocol decoding, or hardware-specific features.
- **Python Plugins**: For extending the functionality with custom scanners, parsers, AI/ML analytics, or automation.
- **Bindings/Adapters**: To integrate with external libraries, hardware, or proprietary protocols.

## Guidelines for Contributing Modules

1. **Performance Critical? Use C++/pybind11:**
    - Place all performance-sensitive code in subfolders with proper documentation and `setup.py` for compilation.
    - Use [pybind11](https://github.com/pybind/pybind11) to expose C++ classes/functions to Python core.

2. **Plugin Architecture:**
    - Follow the standard plugin API as documented in `/docs/`.
    - Implement all hooks for initialization, teardown, and error handling.
    - Respect security sandboxing and privilege separation.

3. **Testing & Documentation:**
    - All modules must include their own tests and clear usage examples.
    - Document dependencies, build steps, and usage in the module’s `README.md`.

4. **Security & Licensing:**
    - Ensure code does not introduce security vulnerabilities.
    - Do not copy GPL or incompatible code without compliance.

## Example Structure

modules/
├── my_native_module/
│ ├── src/
│ ├── setup.py
│ └── README.md
└── my_python_plugin/
├── init.py
└── README.md


## Future Roadmap

- Hardware offloading support (e.g., FPGA, SDR, WiFi radios)
- Vendor-specific drivers and protocol decoders
- AI/ML-based detection modules

