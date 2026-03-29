import os
import subprocess
import sys
import shutil

def launch_terminal(command, title="WiFiNetScanner Scan"):
    for term in ["gnome-terminal", "xterm", "konsole", "xfce4-terminal"]:
        if shutil.which(term):
            if term == "gnome-terminal":
                subprocess.Popen([term, "--", "bash", "-c", f'echo "{title}"; {command}; exec bash'])
            elif term == "xterm":
                subprocess.Popen([term, "-T", title, "-e", f"{command}; bash"])
            elif term == "konsole":
                subprocess.Popen([term, "-e", f"{command}; bash"])
            elif term == "xfce4-terminal":
                subprocess.Popen([term, "--title", title, "-e", f"{command}; bash"])
            return
    print("No supported terminal emulator found.")
    sys.exit(1)

def main_menu():
    while True:
        os.system('clear')
        print("""
        ==========================
        WiFiNetScanner Main Menu
        ==========================
        1. Deep WiFi Scan
        2. Deep Network Scan
        3. ARP Network Scan
        4. Exit
        """)
        choice = input("Choose an option: ").strip()
        if choice == "1":
            iface = input("WiFi interface in monitor mode (e.g., wlan0): ").strip()
            command = f"sudo wifinetscanner --wifi-scan -i {iface}"
            launch_terminal(command, title="WiFi Deep Scan")
            input("WiFi Scan launched. Press Enter to continue...")
        elif choice == "2":
            target = input("Target (IP/domain/range/CIDR): ").strip()
            scan_type = input("Scan type (ip/domain/lan/host): ").strip()
            command = f"sudo wifinetscanner --net-scan -t {target} --scan-type {scan_type}"
            launch_terminal(command, title="Network Deep Scan")
            input("Network Scan launched. Press Enter to continue...")
        elif choice == "3":
            iface = input("Network interface (eth0/wlan0): ").strip()
            iprange = input("Range (CIDR, e.g. 192.168.1.0/24): ").strip()
            command = f"sudo wifinetscanner --arp-scan -i {iface} -r {iprange}"
            launch_terminal(command, title="ARP Scan")
            input("ARP Scan launched. Press Enter to continue...")
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            input("Invalid option. Press Enter to continue...")

if __name__ == "__main__":
    main_menu()

