"""
WiFiNetScanner - HTTP Packet Module
Author: WiFiNetScanner Team

This module provides:
    - Parsing of HTTP requests and responses (from TCP streams or payloads)
    - Extraction of method, URL, headers, status, and body
    - Forensic and reporting support for security analysis

Implements HTTP/1.0 and HTTP/1.1 RFCs (basic parsing, ready for extension).
"""

from typing import Tuple, Dict

class HTTPPacket:
    """
    Parses HTTP request/response payloads for security and forensic analysis.
    """

    def __init__(self, data: bytes):
        self.raw = data
        self.is_request = False
        self.is_response = False
        self.method = None
        self.url = None
        self.status_code = None
        self.reason = None
        self.headers = {}
        self.body = b""
        self.parse()

    def parse(self):
        try:
            text = self.raw.decode(errors="replace")
            lines = text.split("\r\n")
            # Detect request or response
            if lines[0].startswith(("GET ", "POST ", "HEAD ", "PUT ", "DELETE ", "OPTIONS ", "PATCH ")):
                # Request
                self.is_request = True
                parts = lines[0].split()
                if len(parts) >= 2:
                    self.method = parts[0]
                    self.url = parts[1]
            elif lines[0].startswith("HTTP/"):
                # Response
                self.is_response = True
                parts = lines[0].split()
                if len(parts) >= 2:
                    self.status_code = parts[1]
                    self.reason = " ".join(parts[2:])
            # Headers
            idx = 1
            while idx < len(lines):
                if lines[idx] == "":
                    idx += 1
                    break
                if ": " in lines[idx]:
                    k, v = lines[idx].split(": ", 1)
                    self.headers[k.strip()] = v.strip()
                idx += 1
            # Body
            self.body = "\r\n".join(lines[idx:]).encode()
        except Exception:
            pass  # Silently ignore malformed HTTP payloads for now

    def summary(self) -> Dict:
        """
        Return a summary dict for reporting and analysis.
        """
        if self.is_request:
            return {
                "type": "request",
                "method": self.method,
                "url": self.url,
                "headers": self.headers,
                "body_len": len(self.body)
            }
        elif self.is_response:
            return {
                "type": "response",
                "status_code": self.status_code,
                "reason": self.reason,
                "headers": self.headers,
                "body_len": len(self.body)
            }
        else:
            return {"type": "unknown"}

# Example usage:
# http_pkt = HTTPPacket(tcp_payload)
# print(http_pkt.summary())
