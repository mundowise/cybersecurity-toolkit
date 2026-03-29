import pytest
from core.network_scanner import NetworkScanner

@pytest.fixture
def scanner():
    return NetworkScanner()

def test_tcp_scan_closed(scanner):
    assert not scanner.tcp_scan('127.0.0.1', 65000, timeout=0.1)

def test_scan_host(scanner):
    # Use localhost port 80/443 as examples; may vary
    result = scanner.scan_host('127.0.0.1', [80, 9999], timeout=0.1, threads=2)
    assert isinstance(result, dict)
    assert 80 in result and 9999 in result