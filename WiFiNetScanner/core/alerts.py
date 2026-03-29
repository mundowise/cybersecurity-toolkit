"""
WiFiNetScanner - Real-Time Alerts & Rules Engine
Author: WiFiNetScanner Team

Provides rule-based and heuristic alerting for threats, anomalies and relevant events.

Ready for integration in Analyzer or as a plugin system.
"""

import logging

class AlertRule:
    """
    Base class for alert rules. Extend for custom logic.
    """
    def __init__(self, name, description, callback):
        self.name = name
        self.description = description
        self.callback = callback  # Should return (alerted: bool, msg: str) when called with event

    def check(self, event):
        return self.callback(event)

class AlertEngine:
    """
    Core alert engine that applies rules to parsed events in real-time.
    """
    def __init__(self):
        self.rules = []
        self.log = logging.getLogger("WiFiNetScanner.AlertEngine")

    def add_rule(self, rule: AlertRule):
        self.rules.append(rule)

    def process(self, event):
        """
        Check all rules for an event. Returns list of alert messages.
        """
        alerts = []
        for rule in self.rules:
            try:
                triggered, msg = rule.check(event)
                if triggered:
                    alerts.append({"rule": rule.name, "message": msg})
                    self.log.warning(f"ALERT [{rule.name}]: {msg}")
            except Exception as e:
                self.log.error(f"Error in rule {rule.name}: {e}")
        return alerts

# === Ejemplo de reglas básicas ===

def arp_spoofing_rule(event):
    # Detecta si un mismo IP responde con MAC diferente en ARP
    if "arp" in event.get("layers", {}):
        arp = event["layers"]["arp"]
        # Se requiere un historial para comparar, esto es un placeholder de ejemplo
        # (en producción se implementaría con una base de datos de observados)
        if arp["opcode"] == 2 and arp["src_ip"] == "gateway_ip_sospechoso":
            return True, f"Possible ARP spoofing: {arp['src_ip']} has multiple MACs!"
    return False, ""

def icmp_scan_rule(event):
    # Detecta un volumen alto de ICMP Echo Requests
    if "icmp" in event.get("layers", {}):
        icmp = event["layers"]["icmp"]
        if icmp["type"] == 8:
            return True, "ICMP Echo Request detected (possible ping scan)"
    return False, ""

def suspicious_http_rule(event):
    # Detecta User-Agent o URLs sospechosas en HTTP
    http = event.get("layers", {}).get("http")
    if http and http.get("headers"):
        if "sqlmap" in http["headers"].get("User-Agent", "").lower():
            return True, "SQLMap scan detected via User-Agent"
        if "/etc/passwd" in http.get("url", ""):
            return True, "Attempt to access /etc/passwd (possible LFI)"
    return False, ""

# === Ejemplo de integración ===
if __name__ == "__main__":
    # Prueba rápida de motor de alertas
    engine = AlertEngine()
    engine.add_rule(AlertRule("ARP Spoofing", "Detect ARP IP->MAC anomalies", arp_spoofing_rule))
    engine.add_rule(AlertRule("ICMP Scan", "Detect ICMP Echo Requests", icmp_scan_rule))
    engine.add_rule(AlertRule("Suspicious HTTP", "Detect suspicious HTTP headers/paths", suspicious_http_rule))
    test_event = {
        "layers": {
            "http": {"headers": {"User-Agent": "sqlmap"}, "url": "/etc/passwd"},
            "icmp": {"type": 8},
        }
    }
    print(engine.process(test_event))
