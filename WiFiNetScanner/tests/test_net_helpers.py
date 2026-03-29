import pytest
from utils.net_helpers import expand_hosts
import ipaddress

def test_expand_hosts_valid():
    cidr = '192.168.1.0/30'
    hosts = list(expand_hosts(cidr))
    assert hosts == [str(ip) for ip in ipaddress.ip_network(cidr).hosts()]

def test_expand_hosts_invalid(caplog):
    list(expand_hosts('invalid'))
    assert 'Invalid network' in caplog.text