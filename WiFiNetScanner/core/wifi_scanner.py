import os
import time
import threading
import json
from datetime import datetime
import logging

from core.wifi_driver import WiFiDriver
from core.packet_sniffer import PacketSniffer
from core.packet_parser import PacketParser
from core.plugin_loader import PluginLoader
from utils.net_helpers import load_oui, get_vendor, guess_device_type, parse_security, check_vuln
from rich.console import Console
from rich.table import Table

class WiFiScanResult:
    def __init__(self):
        self.networks: dict[str, dict] = {}
        self.clients: dict[str, dict] = {}
        self._lock = threading.Lock()

    def add_network(self, bssid: str, info: dict) -> None:
        with self._lock:
            self.networks[bssid] = info

    def add_client(self, mac: str, info: dict) -> None:
        with self._lock:
            self.clients[mac] = info

class WiFiScanner:
    def __init__(
        self,
        interface: str,
        duration: int = 60,
        channels: list[int] = None,
        plugins_package: str = 'modules'
    ):
        self.interface = interface
        self.duration = duration
        self.channels = channels or [1, 6, 11, 36, 40, 44, 48]
        self.log = logging.getLogger(self.__class__.__name__)
        self.driver = WiFiDriver(interface)
        self.parser = PacketParser()
        self.oui = load_oui(os.path.join(os.path.dirname(__file__), 'oui.txt'))
        self.result = WiFiScanResult()
        self.stop_hopper = threading.Event()

        # Carga dinámica y segura de plugins profesionales
        loader = PluginLoader(plugins_package)
        for plugin in loader.load_plugins():
            try:
                plugin.register(self)
            except Exception as e:
                self.log.error(f"Error al registrar plugin {plugin.__class__.__name__}: {e}")

    def _handle_packet(self, pkt) -> None:
        info = self.parser.parse(pkt)
        if not info:
            return
        if info['protocol'] == 'beacon':
            bssid = info['bssid']
            if bssid not in self.result.networks:
                vendor = get_vendor(bssid, self.oui)
                dtype = guess_device_type(bssid, info['ssid'], vendor)
                security = parse_security(info['payload'])
                vuln = check_vuln(security)
                self.result.add_network(bssid, {
                    'SSID': info['ssid'],
                    'BSSID': bssid,
                    'Channel': info['channel'],
                    'Signal': info['signal'],
                    'Security': security,
                    'Vulnerabilities': vuln,
                    'Vendor': vendor,
                    'DeviceType': dtype,
                    'Clients': []
                })
        elif info['protocol'] == 'data':
            bssid = info['bssid']
            client = info['src']
            if bssid in self.result.networks and client not in self.result.clients:
                vendor = get_vendor(client, self.oui)
                dtype = guess_device_type(client, '', vendor)
                self.result.add_client(client, {
                    'MAC': client,
                    'BSSID': bssid,
                    'Vendor': vendor,
                    'DeviceType': dtype
                })
                self.result.networks[bssid]['Clients'].append(client)

    def _channel_hop(self) -> None:
        while not self.stop_hopper.is_set():
            for ch in self.channels:
                if self.stop_hopper.is_set():
                    break
                self.driver.set_channel(ch)
                time.sleep(3)

    def scan(self) -> None:
        self.log.info(f"Iniciando escaneo Wi-Fi en {self.interface} por {self.duration}s")
        self.driver.set_monitor_mode()
        hopper = threading.Thread(target=self._channel_hop, daemon=True)
        hopper.start()
        sniffer = PacketSniffer(
            interface=self.interface,
            packet_handler=self._handle_packet,
            timeout=self.duration,
            bpf_filter='type mgt or type data'
        )
        sniffer.start()
        sniffer.thread.join()
        self.stop_hopper.set()
        hopper.join()
        self.driver.set_managed_mode()
        self.log.info("Escaneo Wi-Fi finalizado")

    def print_results(self, live: bool = False) -> None:
        console = Console()
        if live:
            console.clear()
        table = Table(title="Redes Wi-Fi")
        for col in ['SSID', 'BSSID', 'Channel', 'Signal', 'Security', 'Vulnerabilities', 'Vendor', 'DeviceType', 'Clients']:
            table.add_column(col)
        for net in self.result.networks.values():
            clients = ",".join(net['Clients'])
            table.add_row(
                net['SSID'], net['BSSID'], str(net['Channel']), str(net['Signal']),
                net['Security'], net['Vulnerabilities'], net['Vendor'], net['DeviceType'], clients
            )
        console.print(table)
        client_table = Table(title="Clientes Conectados")
        for col in ['MAC', 'BSSID', 'Vendor', 'DeviceType']:
            client_table.add_column(col)
        for cli in self.result.clients.values():
            client_table.add_row(cli['MAC'], cli['BSSID'], cli['Vendor'], cli['DeviceType'])
        console.print(client_table)

    def export_report(self, output_dir: str = 'data') -> None:
        os.makedirs(output_dir, exist_ok=True)
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(output_dir, f"scan_wifi_{now}.json")
        report = {
            'networks': self.result.networks,
            'clients': self.result.clients,
            'timestamp': now
        }
        with open(path, 'w') as f:
            json.dump(report, f, indent=2)
        self.log.info(f"Reporte guardado en {path}")



