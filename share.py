"""Quantum FlightPath Optimizer - Live Public Sharing Utility.

Starts a persistent Cloudflare public HTTPS tunnel so your team can access the application from any device without passwords or configuration.
"""

import subprocess
import os
import sys
import time

def main():
    print("=" * 70)
    print("QUANTUM FLIGHTPATH OPTIMIZER - CLOUDFLARE PUBLIC SHARING")
    print("=" * 70)
    print("\nStarting Cloudflare Tunnel on port 5173 with HTTP/2 protocol...")
    print("This provides a direct, secure, zero-password public HTTPS URL.\n")

    exe_path = os.path.join(os.path.dirname(__file__), "cloudflared.exe")
    if not os.path.exists(exe_path):
        exe_path = "cloudflared"

    cmd = [exe_path, "tunnel", "--protocol", "http2", "--url", "http://localhost:5173"]

    while True:
        try:
            proc = subprocess.Popen(cmd)
            proc.wait()
        except KeyboardInterrupt:
            print("\nTunnel stopped by user.")
            break
        except Exception as e:
            print(f"Reconnecting tunnel in 3 seconds... ({e})")
            time.sleep(3)

if __name__ == "__main__":
    main()
