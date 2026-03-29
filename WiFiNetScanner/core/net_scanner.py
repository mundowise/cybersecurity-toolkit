# core/net_scanner.py

import socket
import threading
import json
import os
import sys
import time
from datetime import datetime
from queue import Queue
from utils.net_helpers import expand_cidr, is_valid_ipv4
from rich.console import Console
from rich.table import Table

COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 139, 143, 443, 445, 465, 587, 993, 995, 1723, 3306, 3389, 5900, 8080, 8443]
SERVICE_NAMES = {
    21: "FTP", 22: "SSH", 23: "TELNET", 25: "SMTP", 53: "DNS", 80: "HTTP", 110: "POP3", 139: "NETBIOS", 143: "IMAP",
    443: "HTTPS", 445: "SMB", 465: "SMTPS", 587: "SMTP", 993: "IMAPS", 995: "POP3S", 1723: "PPTP",
    3306: "MYSQL", 3389: "RDP", 5900: "VNC", 8080: "HTTP-ALT", 8443: "HTTPS-ALT"
}

def resolve_domain(domain):
    try:
        return socket.gethostbyname(domain)
    except Exception:
        return None

def banner_grab(ip, port, timeout=2):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, port))
        s.sendall(b"\r\n")
        banner = s.recv(1024)
        s.close()
        return banner.decode(errors="replace").strip()
    except Exception:
        return ""

def detect_os(ttl, banner):
    # TTL typical: Windows=128, Linux=64, Cisco=255
    if banner:
        b = banner.lower()
        if "iis" in b or "asp.net" in b:
            return "Windows/IIS"
        if "apache" in b:
            return "Linux/Apache"
        if "debian" in b or "ubuntu" in b:
            return "Linux (Debian/Ubuntu)"
        if "centos" in b or "fedora" in b:
            return "Linux (RedHat)"
        if "samba" in b:
            return "Linux/Samba"
    if ttl >= 128:
        return "Windows"
    elif ttl >= 64:
        return "Linux/Unix"
    elif ttl >= 254:
        return "Cisco/Network"
    else:
        return "Unknown"

def traceroute(target, max_hops=16):
    hops = []
    try:
        for ttl in range(1, max_hops+1):
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(1)
            s.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
            s.sendto(b'', (target, 33434))
            try:
                data, curr_addr = s.recvfrom(512)
                curr_addr = curr_addr[0]
            except socket.timeout:
                curr_addr = "*"
            s.close()
            hops.append(curr_addr)
            if curr_addr == target:
                break
    except Exception:
        pass
    return hops

class NetScanResult:
    def __init__(self):
        self.hosts = {}
        self._lock = threading.Lock()
    def add_result(self, ip, info):
        with self._lock:
            self.hosts[ip] = info

def deep_network_scan(target, scan_type="ip", ports=COMMON_PORTS, threads=50):
    """
    Escaneo de red profundo y profesional.
    """
    console = Console()
    print(f"\n[*] Iniciando escaneo profundo de red sobre: {target} (tipo: {scan_type})\n")
    targets = []
    if scan_type == "ip":
        targets = [target]
    elif scan_type == "domain":
        ip = resolve_domain(target)
        if ip:
            targets = [ip]
        else:
            print(f"[!] No se pudo resolver {target}")
            return
    elif scan_type == "lan" or "/" in target:
        targets = expand_cidr(target)
    elif scan_type == "host":
        try:
            with open(target) as f:
                for line in f:
                    ip = line.strip()
                    if is_valid_ipv4(ip):
                        targets.append(ip)
        except Exception:
            print(f"[!] Archivo de hosts inválido: {target}")
            return
    else:
        print("[!] Tipo de escaneo desconocido.")
        return

    result = NetScanResult()
    q = Queue()
    for ip in targets:
        q.put(ip)

    def worker():
        while not q.empty():
            ip = q.get()
            info = scan_host(ip, ports)
            result.add_result(ip, info)
            show_table(result, live=True)
            q.task_done()

    threads_list = []
    for _ in range(min(threads, len(targets))):
        t = threading.Thread(target=worker)
        t.daemon = True
        threads_list.append(t)
        t.start()

    try:
        while any(t.is_alive() for t in threads_list):
            time.sleep(1)
    except KeyboardInterrupt:
        print("[!] Escaneo interrumpido por usuario.")

    show_table(result, live=False)
    export_net_report(result)
    print("\n[*] Escaneo de red finalizado. Reporte completo en /data.")

def scan_host(ip, ports):
    info = {
        "ip": ip,
        "ports": [],
        "os_guess": "",
        "services": [],
        "banner": "",
        "ttl": "",
        "traceroute": []
    }
    open_ports = []
    for port in ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        try:
            s.connect((ip, port))
            try:
                s.sendall(b"\r\n")
                banner = s.recv(1024)
                banner = banner.decode(errors="replace").strip()
            except Exception:
                banner = ""
            info["ports"].append({"port": port, "status": "open", "service": SERVICE_NAMES.get(port, ""), "banner": banner})
            info["services"].append(SERVICE_NAMES.get(port, ""))
            if banner and not info["banner"]:
                info["banner"] = banner
            open_ports.append(port)
        except Exception:
            info["ports"].append({"port": port, "status": "closed", "service": SERVICE_NAMES.get(port, "")})
        finally:
            try:
                info["ttl"] = s.getsockopt(socket.IPPROTO_IP, socket.IP_TTL)
            except Exception:
                info["ttl"] = ""
            s.close()
    # Detección básica de OS y traceroute si hay algún puerto abierto
    if open_ports:
        info["traceroute"] = traceroute(ip)
        info["os_guess"] = detect_os(info["ttl"] if info["ttl"] else 0, info["banner"])
    return info

def show_table(result, live=False):
    table = Table(title="Host/Service Scan", show_lines=True)
    table.add_column("IP")
    table.add_column("Open Ports")
    table.add_column("Services")
    table.add_column("OS Guess")
    table.add_column("Traceroute")
    for ip, info in result.hosts.items():
        open_ports = ",".join(str(p["port"]) for p in info["ports"] if p["status"] == "open")
        services = ",".join(info["services"])
        traceroute = "->".join(info["traceroute"]) if info["traceroute"] else "-"
        table.add_row(ip, open_ports, services, info["os_guess"], traceroute)
    console = Console()
    if live:
        console.clear()
    console.print(table)

def export_net_report(result):
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("data", exist_ok=True)
    report = {
        "hosts": result.hosts,
        "timestamp": now,
    }
    path = f"data/scan_net_{now}.json"
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"[*] Reporte guardado en {path}")
