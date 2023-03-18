import os
import socket
from dnslib import DNSRecord, RR, A, QTYPE
from dnslib.server import DNSServer, BaseResolver
from ping3 import ping
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests


class RandomIPResolver(BaseResolver):
    def __init__(self, num_workers=8):
        self.num_workers = num_workers

    def resolve(self, request, handler):
        reply = request.reply()
        q = request.q
        if q.qtype == QTYPE.A:
            ip = self._generate_valid_ip()
            reply.add_answer(
                RR(rname=q.qname, rtype=QTYPE.A, rdata=A(ip), ttl=60))
        return reply

    def _generate_valid_ip(self):
        while True:
            with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
                futures = {executor.submit(
                    self._is_ip_valid, ip): ip for ip in self._generate_random_ips()}
                for future in as_completed(futures):
                    if future.result():
                        return futures[future]

    def _generate_random_ips(self):
        ips = []
        for _ in range(self.num_workers):
            ip = f'{os.urandom(1)[0]}.{os.urandom(1)[0]}.{os.urandom(1)[0]}.{os.urandom(1)[0]}'
            ips.append(ip)
        return ips

    def _is_ip_valid(self, ip):
        if self._is_ip_responsive(ip) and self._ip_returns_html_page(ip):
            return True
        return False

    def _is_ip_responsive(self, ip):
        try:
            response_time = ping(ip, timeout=0.5)
            return response_time is not None
        except socket.error:
            return False

    def _ip_returns_html_page(self, ip):
        try:
            response = requests.get(f'http://{ip}', timeout=0.5)
            content_type = response.headers.get('Content-Type', '').lower()
            return 'text/html' in content_type
        except (requests.exceptions.RequestException, socket.error):
            return False


def main():
    resolver = RandomIPResolver()
    server = DNSServer(resolver, port=53, address='0.0.0.0')
    print("Starting DNS server...")
    server.start()


if __name__ == '__main__':
    main()
