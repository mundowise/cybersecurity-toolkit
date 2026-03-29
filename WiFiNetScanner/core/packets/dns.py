"""
WiFiNetScanner - DNS Packet Module
Author: WiFiNetScanner Team

This module provides:
    - Parsing of DNS request/response packets
    - Support for standard queries, responses, and common extensions
    - Extraction of queries, answers, types, and flags for security and forensic analysis

Implements RFC 1035 and basic extensions.
"""

import struct

class DNSPacket:
    """
    DNS packet parser for analysis and reporting.
    """

    def __init__(self, data: bytes):
        self.raw = data
        self.header = None
        self.questions = []
        self.answers = []
        self.authority = []
        self.additional = []
        self.parse()

    def parse(self):
        try:
            (self.id, flags, qdcount, ancount, nscount, arcount) = struct.unpack("!HHHHHH", self.raw[:12])
            self.qr = (flags >> 15) & 1
            self.opcode = (flags >> 11) & 0xF
            self.aa = (flags >> 10) & 1
            self.tc = (flags >> 9) & 1
            self.rd = (flags >> 8) & 1
            self.ra = (flags >> 7) & 1
            self.rcode = flags & 0xF

            offset = 12
            # Questions
            for _ in range(qdcount):
                qname, offset = self._read_name(offset)
                qtype, qclass = struct.unpack("!HH", self.raw[offset:offset+4])
                offset += 4
                self.questions.append({
                    "qname": qname,
                    "qtype": qtype,
                    "qclass": qclass
                })
            # Answers, Authority, Additional - stub (expand as needed)
            # Full implementation can parse all RRs; for brevity, only Qs here
        except Exception as e:
            self.header = {"parse_error": str(e)}

    def _read_name(self, offset):
        labels = []
        length = self.raw[offset]
        while length != 0:
            if (length & 0xC0) == 0xC0:
                # Pointer to another part of the packet
                pointer = struct.unpack("!H", self.raw[offset:offset+2])[0] & 0x3FFF
                label, _ = self._read_name(pointer)
                labels.append(label)
                offset += 2
                return ".".join(labels), offset
            else:
                labels.append(self.raw[offset+1:offset+1+length].decode(errors="replace"))
                offset += length + 1
                length = self.raw[offset]
        return ".".join(labels), offset+1

    def get_queries(self):
        """
        Returns a list of queries in the packet.
        """
        return self.questions

    def summary(self):
        """
        Return a summary of the DNS packet for reporting.
        """
        if self.header and "parse_error" in self.header:
            return {"error": self.header["parse_error"]}
        return {
            "id": self.id,
            "qr": self.qr,
            "opcode": self.opcode,
            "aa": self.aa,
            "tc": self.tc,
            "rd": self.rd,
            "ra": self.ra,
            "rcode": self.rcode,
            "queries": self.questions,
            # Add answers/authority/additional as needed
        }

# Example usage:
# dns_pkt = DNSPacket(raw_bytes)
# print(dns_pkt.summary())
