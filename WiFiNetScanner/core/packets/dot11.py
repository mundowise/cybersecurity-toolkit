import struct

def mac_bytes_to_str(mac: bytes) -> str:
    return ":".join(f"{b:02x}" for b in mac)

def mac_str_to_bytes(mac: str) -> bytes:
    return bytes(int(x, 16) for x in mac.split(":"))

class Dot11Frame:
    def __init__(self, frame_control: int, duration: int, addr1: str, addr2: str, addr3: str,
                 seq_ctrl: int = 0, payload: bytes = b"", fcs: int = None):
        self.frame_control = frame_control
        self.duration = duration
        self.addr1 = addr1
        self.addr2 = addr2
        self.addr3 = addr3
        self.seq_ctrl = seq_ctrl
        self.payload = payload
        self.fcs = fcs

    def build(self) -> bytes:
        hdr = struct.pack(
            "<HH6s6s6sH",
            self.frame_control,
            self.duration,
            mac_str_to_bytes(self.addr1),
            mac_str_to_bytes(self.addr2),
            mac_str_to_bytes(self.addr3),
            self.seq_ctrl
        )
        frame = hdr + self.payload
        if self.fcs is not None:
            frame += struct.pack("<I", self.fcs)
        return frame

    @staticmethod
    def parse(raw: bytes):
        if len(raw) < 24:
            print(f"[WARN] Frame too short for Dot11Frame.parse: {len(raw)} bytes")
            raise ValueError("802.11 frame too short")
        try:
            fc, dur, addr1, addr2, addr3, seq_ctrl = struct.unpack("<HH6s6s6sH", raw[:24])
            payload = raw[24:-4] if len(raw) > 28 else raw[24:]
            fcs = struct.unpack("<I", raw[-4:])[0] if len(raw) > 28 else None
            return {
                "frame_control": fc,
                "duration": dur,
                "addr1": mac_bytes_to_str(addr1),
                "addr2": mac_bytes_to_str(addr2),
                "addr3": mac_bytes_to_str(addr3),
                "seq_ctrl": seq_ctrl,
                "payload": payload,
                "fcs": fcs,
                "type": Dot11Frame.get_type(fc),
                "subtype": Dot11Frame.get_subtype(fc),
            }
        except Exception as e:
            print(f"[ERROR] Exception in Dot11Frame.parse: {e}")
            raise

    @staticmethod
    def get_type(frame_control: int) -> str:
        frame_type = (frame_control >> 2) & 0b11
        return ["Management", "Control", "Data", "Reserved"][frame_type]

    @staticmethod
    def get_subtype(frame_control: int) -> str:
        frame_type = (frame_control >> 2) & 0b11
        subtype = (frame_control >> 4) & 0b1111
        subtype_names = {
            0: {
                0: "Association Request",
                1: "Association Response",
                2: "Reassociation Request",
                3: "Reassociation Response",
                4: "Probe Request",
                5: "Probe Response",
                8: "Beacon"
            },
            2: {
                0: "Data"
            }
        }
        return subtype_names.get(frame_type, {}).get(subtype, f"Unknown_{subtype}")
