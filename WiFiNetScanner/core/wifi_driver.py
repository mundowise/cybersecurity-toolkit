import logging
import platform
import subprocess
import netifaces


class WiFiDriver:
    """
    Advanced WiFi interface controller for packet capture and channel management.
    Uses safe subprocess calls to system utilities without shell interpolation.
    """

    def __init__(self, interface: str):
        self.interface = interface
        self.log = logging.getLogger(self.__class__.__name__)
        self.os_type = platform.system().lower()
        self._validate_interface()

    def _validate_interface(self) -> None:
        if self.os_type != 'linux':
            self.log.error(f"OS '{self.os_type}' not supported for WiFiDriver")
            raise NotImplementedError('Only Linux is supported')
        if self.interface not in netifaces.interfaces():
            self.log.error(f"Interface '{self.interface}' not found")
            raise ValueError(f"Interface '{self.interface}' not found")

    def _run_command(self, cmd: list[str]) -> str:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()

    def set_monitor_mode(self) -> bool:
        self.log.info(f"Setting '{self.interface}' to monitor mode")
        try:
            self._run_command(['ip', 'link', 'set', self.interface, 'down'])
            self._run_command(['iw', 'dev', self.interface, 'set', 'monitor', 'none'])
            self._run_command(['ip', 'link', 'set', self.interface, 'up'])
            self.log.info(f"Interface '{self.interface}' is now in monitor mode")
            return True
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.strip() if e.stderr else str(e)
            self.log.error(f"Monitor mode failed: {stderr}")
            return False

    def set_managed_mode(self) -> bool:
        self.log.info(f"Setting '{self.interface}' to managed mode")
        try:
            self._run_command(['ip', 'link', 'set', self.interface, 'down'])
            self._run_command(['iw', 'dev', self.interface, 'set', 'type', 'managed'])
            self._run_command(['ip', 'link', 'set', self.interface, 'up'])
            self.log.info(f"Interface '{self.interface}' is now in managed mode")
            return True
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.strip() if e.stderr else str(e)
            self.log.error(f"Managed mode failed: {stderr}")
            return False

    def set_channel(self, channel: int) -> bool:
        self.log.info(f"Setting channel {channel} on '{self.interface}'")
        try:
            self._run_command(['iw', 'dev', self.interface, 'set', 'channel', str(channel)])
            self.log.info(f"Channel set to {channel}")
            return True
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.strip() if e.stderr else str(e)
            self.log.error(f"Channel change failed: {stderr}")
            return False

    def is_interface_up(self) -> bool:
        try:
            out = self._run_command(['ip', 'link', 'show', self.interface])
            return 'UP' in out and self.interface in out
        except Exception:
            return False

    def get_interface_info(self) -> dict:
        info = {'interface': self.interface}
        try:
            out = self._run_command(['iw', 'dev', self.interface, 'info'])
            for line in out.splitlines():
                line = line.strip()
                if line.startswith('type '):
                    info['mode'] = line.split('type ')[1]
                elif line.startswith('channel '):
                    info['channel'] = int(line.split('channel ')[1].split()[0])
                elif line.startswith('addr '):
                    info['mac'] = line.split('addr ')[1]
        except Exception as e:
            self.log.warning(f"Failed to get interface info: {e}")
        return info

