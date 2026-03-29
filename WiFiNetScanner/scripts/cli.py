import typer
from core.wifi_scanner import WiFiScanner
from core.network_scanner import NetworkScanner
from core.arp_scanner import ARPScanner
from rich.console import Console
from rich.table import Table

app = typer.Typer(name="wifinetscanner", help="WiFiNetScanner: unified CLI for network auditing")

@app.command("wifi-scan")
def wifi_scan(
    iface: str = typer.Option(..., "--iface", "-i", help="Wireless interface to use"),
    duration: int = typer.Option(60, "--duration", "-d", help="Scan duration in seconds"),
    channels: str = typer.Option("", "--channels", "-c", help="Comma-separated list of channels (e.g. 1,6,11)")
):
    """Deep Wi-Fi scan to discover networks and clients."""
    ch_list = [int(ch) for ch in channels.split(",") if ch] if channels else None
    scanner = WiFiScanner(interface=iface, duration=duration, channels=ch_list)
    scanner.scan()
    scanner.print_results(live=True)
    scanner.export_report()

@app.command("net-scan")
def net_scan(
    target: str = typer.Option(..., "--target", "-t", help="IP, CIDR network, or domain to scan"),
    scan_type: str = typer.Option("ip", "--type", "-s", help="Scan type: ip|lan|domain"),
    ports: str = typer.Option("", "--ports", "-p", help="Comma-separated list of ports (e.g. 22,80,443)"),
    timeout: float = typer.Option(1.0, "--timeout", help="Connection timeout in seconds"),
    threads: int = typer.Option(100, "--threads", help="Number of parallel threads")
):
    """Deep network TCP port scan."""
    ports_list = [int(p) for p in ports.split(",") if p] if ports else None
    scanner = NetworkScanner()
    results = scanner.deep_network_scan(target, scan_type, ports_list, timeout, threads)
    typer.echo(results)

@app.command("arp-scan")
def arp_scan(
    iface: str = typer.Option(..., "--iface", "-i", help="Interfaz para realizar escaneo ARP"),
    network: str = typer.Option(..., "--network", "-n", help="Rango CIDR de la red local")
):
    """Escaneo ARP rápido en redes locales."""
    scanner = ARPScanner(interface=iface)
    hosts = scanner.scan(network)
    table = Table(title="Resultados ARP Scan")
    for col in ["IP", "MAC", "Vendor"]:
        table.add_column(col)
    for host in hosts:
        table.add_row(host["IP"], host["MAC"], host["Vendor"])
    console = Console()
    console.print(table)

if __name__ == "__main__":
    app()