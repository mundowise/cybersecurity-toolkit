from setuptools import setup, find_packages

setup(
    name="wifinetscanner",
    version="1.0.0",
    description="Advanced Wi-Fi and network auditing tool",
    author="Your Name",
    packages=find_packages(exclude=["tests*", "scripts*", "docs*"]),
    install_requires=[
        "scapy>=2.4",
        "rich>=10.0",
        "netifaces>=0.10",
        "typer>=0.6",
    ],
    entry_points={
        "console_scripts": [
            "wifinetscanner=scripts.cli:app",
        ],
    },
    python_requires='>=3.10',
)

