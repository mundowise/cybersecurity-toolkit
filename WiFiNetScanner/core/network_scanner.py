import socket
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

from utils.net_helpers import expand_hosts


class NetworkScanner:
    """
    Performs TCP port scans with IPv4/IPv6 support.
    """

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

    def tcp_scan(self, host: str, port: int, timeout: float = 1.0) -> bool:
        try:
            infos = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
            for family, _, _, _, addr in infos:
                with socket.socket(family, socket.SOCK_STREAM) as s:
                    s.settimeout(timeout)
                    try:
                        s.connect(addr)
                        return True
                    except (socket.timeout, ConnectionRefusedError):
                        continue
        except Exception as e:
            self.log.debug(f"TCP scan error on {host}:{port} - {e}")
        return False

    def scan_host(self, host: str, ports: List[int], timeout: float, threads: int) -> Dict[int, bool]:
        results: Dict[int, bool] = {}
        with ThreadPoolExecutor(max_workers=threads) as executor:
            future_map = {executor.submit(self.tcp_scan, host, p, timeout): p for p in ports}
            for future in as_completed(future_map):
                results[future_map[future]] = future.result()
        return results

    def deep_network_scan(
        self,
        target: str,
        scan_type: str = 'ip',
        ports: List[int] = None,
        timeout: float = 1.0,
        threads: int = 100
    ) -> Dict[str, Dict[int, bool]]:
        if scan_type == 'lan':
            hosts = list(expand_hosts(target))
        elif scan_type == 'ip':
            hosts = [target]
        elif scan_type == 'domain':
            hosts = list({info[4][0] for info in socket.getaddrinfo(target, None)})
        else:
            self.log.error(f"Unsupported scan_type '{scan_type}'")
            return {}
        if ports is None:
            ports = [21,22,23,80,443,3389]
        results = {}
        for h in hosts:
            self.log.info(f"Scanning {h}...")
            results[h] = self.scan_host(h, ports, timeout, threads)
        return results
