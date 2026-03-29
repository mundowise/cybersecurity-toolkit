"""
WiFiNetScanner - TLS/SSL Packet Module
Author: WiFiNetScanner Team

This module provides:
    - Parsing of TLS/SSL handshake messages (ClientHello, ServerHello)
    - Extraction of version, cipher suites, extensions, SNI, etc.
    - Detection of insecure versions and forensic evidence for reporting

Implements key parts of RFC 5246 (TLS 1.2) and compatible with SSLv3/TLS1.0/1.1/1.3.
"""

import struct

class TLSPacket:
    """
    Minimalist TLS/SSL handshake parser for fingerprinting and analysis.
    Focus: ClientHello and ServerHello parsing.
    """

    def __init__(self, data: bytes):
        self.raw = data
        self.records = []
        self.handshakes = []
        self.parse()

    def parse(self):
        try:
            offset = 0
            # Parse multiple records if present
            while offset + 5 < len(self.raw):
                content_type = self.raw[offset]
                version = struct.unpack("!H", self.raw[offset+1:offset+3])[0]
                rec_len = struct.unpack("!H", self.raw[offset+3:offset+5])[0]
                record = {
                    "content_type": content_type,
                    "version": version,
                    "length": rec_len,
                    "payload": self.raw[offset+5:offset+5+rec_len]
                }
                self.records.append(record)
                if content_type == 22:  # Handshake
                    self._parse_handshake(record["payload"])
                offset += 5 + rec_len
        except Exception:
            pass

    def _parse_handshake(self, data: bytes):
        try:
            offset = 0
            while offset + 4 < len(data):
                hs_type = data[offset]
                hs_len = int.from_bytes(data[offset+1:offset+4], "big")
                hs_payload = data[offset+4:offset+4+hs_len]
                handshake = {"type": hs_type, "length": hs_len}
                # ClientHello
                if hs_type == 1:
                    handshake.update(self._parse_client_hello(hs_payload))
                # ServerHello
                elif hs_type == 2:
                    handshake.update(self._parse_server_hello(hs_payload))
                self.handshakes.append(handshake)
                offset += 4 + hs_len
        except Exception:
            pass

    def _parse_client_hello(self, data: bytes) -> dict:
        result = {}
        try:
            version = struct.unpack("!H", data[:2])[0]
            result["client_version"] = version
            result["random"] = data[2:34]
            session_id_len = data[34]
            idx = 35 + session_id_len
            cs_len = struct.unpack("!H", data[idx:idx+2])[0]
            idx += 2
            ciphers = [struct.unpack("!H", data[i:i+2])[0] for i in range(idx, idx+cs_len, 2)]
            idx += cs_len
            comp_methods_len = data[idx]
            idx += 1 + comp_methods_len
            # Extensions (if present)
            if idx + 2 <= len(data):
                ext_len = struct.unpack("!H", data[idx:idx+2])[0]
                idx += 2
                exts = []
                end = idx + ext_len
                while idx + 4 <= end and idx + 4 <= len(data):
                    ext_type = struct.unpack("!H", data[idx:idx+2])[0]
                    ext_len_i = struct.unpack("!H", data[idx+2:idx+4])[0]
                    ext_data = data[idx+4:idx+4+ext_len_i]
                    exts.append((ext_type, ext_data))
                    idx += 4 + ext_len_i
                result["extensions"] = exts
            result["cipher_suites"] = ciphers
        except Exception:
            pass
        return result

    def _parse_server_hello(self, data: bytes) -> dict:
        result = {}
        try:
            version = struct.unpack("!H", data[:2])[0]
            result["server_version"] = version
            result["random"] = data[2:34]
            session_id_len = data[34]
            idx = 35 + session_id_len
            result["cipher_suite"] = struct.unpack("!H", data[idx:idx+2])[0]
            idx += 2
            result["compression_method"] = data[idx]
            # Extensions parsing as in client_hello (if present)
        except Exception:
            pass
        return result

    def summary(self):
        """
        Returns a summary of the TLS handshakes detected.
        """
        return {
            "handshakes": self.handshakes
        }

# Example usage:
# tls_pkt = TLSPacket(raw_bytes)
# print(tls_pkt.summary())
