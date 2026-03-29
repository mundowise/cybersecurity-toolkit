import threading
import logging
from scapy.all import sniff, conf


class PacketSniffer:
    def __init__(
        self,
        interface: str,
        packet_handler,
        timeout: int = None,
        bpf_filter: str = None
    ):
        self.interface = interface
        self.packet_handler = packet_handler
        self.timeout = timeout
        self.bpf_filter = bpf_filter
        self.thread = None
        self.log = logging.getLogger(self.__class__.__name__)
        self.running = False

    def _sniff(self) -> None:
        try:
            conf.iface = self.interface
            self.log.info(f"Starting sniff on '{self.interface}' with filter '{self.bpf_filter}'")
            sniff(
                iface=self.interface,
                prn=self._scapy_handler,
                filter=self.bpf_filter,
                timeout=self.timeout,
                store=False
            )
        except Exception as e:
            self.log.error(f"Error during sniffing: {e}")
        finally:
            self.running = False
            self.log.info("Sniffer thread ending")

    def _scapy_handler(self, pkt) -> None:
        try:
            self.packet_handler(pkt)
        except Exception as e:
            self.log.error(f"Handler error: {e}")

    def start(self) -> None:
        if self.running:
            self.log.warning("PacketSniffer already running")
            return
        self.running = True
        self.thread = threading.Thread(target=self._sniff, daemon=True)
        self.thread.start()
        self.log.info("Packet sniffer started")

    def stop(self) -> None:
        if not self.running:
            self.log.warning("PacketSniffer is not running")
            return
        self.running = False
        if self.thread:
            self.thread.join()
        self.log.info("Packet sniffer stopped")

    def is_running(self) -> bool:
        return self.running


