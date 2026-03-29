import logging
from scapy.all import ARP, Ether, srp
from typing import List, Dict

from utils.net_helpers import expand_hosts, load_oui, get_vendor


class ARPScanner:
    """
    Escáner ARP profesional para auditorías rápidas en redes locales.
    """

    def __init__(self, interface: str, timeout: int = 2):
        self.interface = interface
        self.timeout = timeout
        self.log = logging.getLogger(self.__class__.__name__)
        self.oui = load_oui()

    def scan(self, target_network: str) -> List[Dict[str, str]]:
        self.log.info(f"Iniciando escaneo ARP en la red: {target_network}")
        hosts = expand_hosts(target_network)
        answered_list = []

        for host in hosts:
            pkt = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=host)
            ans, _ = srp(pkt, timeout=self.timeout, iface=self.interface, verbose=0)
            for _, received in ans:
                mac = received.hwsrc
                vendor = get_vendor(mac, self.oui)
                self.log.debug(f"Host detectado: IP={received.psrc}, MAC={mac}, Vendor={vendor}")
                answered_list.append({
                    "IP": received.psrc,
                    "MAC": mac,
                    "Vendor": vendor
                })

        self.log.info(f"Escaneo ARP completado, hosts encontrados: {len(answered_list)}")
        return answered_list