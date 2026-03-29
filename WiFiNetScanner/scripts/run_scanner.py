import argparse

def main():
    parser = argparse.ArgumentParser(description="WiFiNetScanner - Professional Suite")
    parser.add_argument("--wifi-scan", action="store_true", help="Deep WiFi scan (monitor mode required)")
    parser.add_argument("--net-scan", action="store_true", help="Deep network scan (LAN/Internet)")
    parser.add_argument("--arp-scan", action="store_true", help="ARP scan (local LAN, fast)")
    parser.add_argument("-i", "--interface", help="Network interface to use (e.g., wlan0, eth0)")
    parser.add_argument("-t", "--target", help="Target IP/domain/CIDR (for network scan)")
    parser.add_argument("-r", "--range", help="IP range/CIDR (for ARP scan)")
    parser.add_argument("--scan-type", help="Type of network scan: ip/domain/lan/host", default="ip")
    args = parser.parse_args()

    if args.wifi_scan:
        from core.wifi_scanner import deep_wifi_scan
        if not args.interface:
            print("Please specify --interface for WiFi scan.")
            return
        deep_wifi_scan(interface=args.interface)
    elif args.arp_scan:
        from core.network_scanner import arp_scan
        if not args.interface or not args.range:
            print("Please specify both --interface and --range for ARP scan.")
            return
        arp_scan(interface=args.interface, cidr=args.range)
    elif args.net_scan:
        from core.net_scanner import deep_network_scan
        if not args.target:
            print("Please specify --target for Network scan.")
            return
        deep_network_scan(target=args.target, scan_type=args.scan_type)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

