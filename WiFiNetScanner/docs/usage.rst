Usage Guide
===========

Command-line usage
------------------

Run a standard Wi-Fi scan for 60 s on interface wlan1:

.. code-block:: bash

   python -m scripts.run_scanner --iface wlan1 --duration 60

API usage
---------

Embed the scanner in tu propio código Python:

.. code-block:: python

   from core.wifi_scanner import WiFiScanner

   scanner = WiFiScanner(interface='wlan1', duration=30)
   scanner.scan()
   scanner.print_results()
   scanner.export_report('./reports')
