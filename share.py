"""Quantum FlightPath Optimizer - Live Public Sharing Utility.

Starts a persistent public HTTPS tunnel so your team can access the application from any device.
"""

import subprocess
import urllib.request
import time
import sys

def get_public_ip():
    try:
        return urllib.request.urlopen("https://api.ipify.org", timeout=5).read().decode().strip()
    except Exception:
        return "Check https://loca.lt/mytunnelpassword"

def main():
    print("=" * 60)
    print("QUANTUM FLIGHTPATH OPTIMIZER - TEAM SHARING UTILITY")
    print("=" * 60)
    
    ip = get_public_ip()
    print(f"\nYour Host IP / Tunnel Password: {ip}")
    print("\nStarting public HTTPS tunnel on port 5173...")
    print("Share this link with your team:\n")
    print("  👉 https://quantum-flightpath.loca.lt")
    print(f"  🔑 Tunnel Password (if prompted): {ip}")
    print("\nLocal Network (Same Wi-Fi):")
    print("  👉 http://192.168.31.60:5173 (No password needed)\n")
    print("=" * 60)
    print("Press Ctrl+C to stop sharing.\n")

    cmd = ["npx.cmd", "localtunnel", "--port", "5173", "--subdomain", "quantum-flightpath"]
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
