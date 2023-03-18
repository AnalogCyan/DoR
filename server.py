import os
import socket
import logging
import time
from dnslib import DNSRecord, RR, A, QTYPE
from dnslib.server import DNSServer, BaseResolver
import requests
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class RandomIPResolver(BaseResolver):
    def __init__(self, num_workers=10):
        self.executor = ThreadPoolExecutor(max_workers=num_workers)

    def is_valid_ip(self, ip):
        try:
            response = requests.get(f'http://{ip}', timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def find_valid_ip(self):
        valid_ip = None
        while not valid_ip:
            ips = [
                f'{os.urandom(1)[0]}.{os.urandom(1)[0]}.{os.urandom(1)[0]}.{os.urandom(1)[0]}' for _ in range(10)]
            results = list(self.executor.map(self.is_valid_ip, ips))
            for ip, is_valid in zip(ips, results):
                if is_valid:
                    valid_ip = ip
                    break
        return valid_ip

    def resolve(self, request, handler):
        reply = request.reply()
        q = request.q
        if q.qtype == QTYPE.A:
            logger.debug('Resolving IP address for query: %s', q.qname)
            start_time = time.time()
            ip = self.find_valid_ip()
            elapsed_time = time.time() - start_time
            logger.debug(
                'Found valid IP: %s (elapsed time: %.2f seconds)', ip, elapsed_time)
            reply.add_answer(
                RR(rname=q.qname, rtype=QTYPE.A, rdata=A(ip), ttl=60))
        return reply

    def shutdown(self):
        self.executor.shutdown()


def main():
    resolver = RandomIPResolver()
    server = DNSServer(resolver, port=53, address='0.0.0.0')
    logger.info("Starting DNS server...")

    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("Shutting down DNS server...")
        resolver.shutdown()
        server.stop()


if __name__ == '__main__':
    main()
