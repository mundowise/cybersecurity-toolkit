"""
WiFiNetScanner - Advanced Reporting and Export Module
Author: WiFiNetScanner Team

Generates, filters, and exports reports in JSON, CSV, TXT, and supports custom templates for SIEM, HTML, PDF, etc.

Ready for direct use in CLI, UI/TUI, REST API, or automated pipelines.
"""

import json
import csv

class Reporter:
    def __init__(self, events):
        """
        Args:
            events (list): List of event/result dicts (as produced by Analyzer or Scanner)
        """
        self.events = events

    def filter_events(self, filter_fn=None):
        """
        Optionally filter events before exporting.
        Args:
            filter_fn (callable): Function that takes an event and returns True/False.
        Returns:
            list: Filtered list of events.
        """
        if filter_fn:
            return [e for e in self.events if filter_fn(e)]
        return self.events

    def to_json(self, filepath=None, filter_fn=None, indent=2):
        data = self.filter_events(filter_fn)
        out = json.dumps(data, indent=indent)
        if filepath:
            with open(filepath, "w") as f:
                f.write(out)
        return out

    def to_csv(self, filepath=None, filter_fn=None):
        data = self.filter_events(filter_fn)
        # Flatten for CSV (customizable per protocol/type)
        rows = []
        for ev in data:
            flat = {
                "timestamp": ev.get("timestamp"),
                "interface": ev.get("interface"),
                "src_addr": ev.get("src_addr"),
            }
            # Extract protocol info (example: TCP/UDP/DNS/HTTP)
            for layer, value in ev.get("layers", {}).items():
                if isinstance(value, dict):
                    for k, v in value.items():
                        flat[f"{layer}_{k}"] = str(v)
            rows.append(flat)
        if not rows:
            return ""
        keys = sorted(set().union(*rows))
        if filepath:
            with open(filepath, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                for row in rows:
                    writer.writerow(row)
        return rows

    def to_txt(self, filepath=None, filter_fn=None):
        data = self.filter_events(filter_fn)
        lines = []
        for ev in data:
            lines.append("="*40)
            lines.append(f"Timestamp: {ev.get('timestamp')}")
            lines.append(f"Interface: {ev.get('interface')}")
            lines.append(f"Source: {ev.get('src_addr')}")
            for layer, value in ev.get("layers", {}).items():
                lines.append(f"--- {layer.upper()} ---")
                if isinstance(value, dict):
                    for k, v in value.items():
                        lines.append(f"{k}: {v}")
                else:
                    lines.append(str(value))
            if ev.get("alerts"):
                lines.append(f"ALERTS: {ev.get('alerts')}")
        out = "\n".join(lines)
        if filepath:
            with open(filepath, "w") as f:
                f.write(out)
        return out

    # Future: to_html(), to_pdf(), to_pcap(), to_siem(), anonymize(), etc.

# Ejemplo de uso:
# reporter = Reporter(events)
# reporter.to_json("report.json")
# reporter.to_csv("report.csv")
# print(reporter.to_txt())
