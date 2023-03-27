import os
import socket
import logging
import time
import json
import random
from dnslib import DNSRecord, RR, A, QTYPE
from dnslib.server import DNSServer, BaseResolver
import requests
from concurrent.futures import ThreadPoolExecutor
from ip_generator import main as generate_ip_data
import pathlib

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class RandomIPResolver(BaseResolver):
    def __init__(self, num_workers=10, json_file="ip_data.json"):
        self.executor = ThreadPoolExecutor(max_workers=num_workers)
        self.json_file = json_file
        self._load_ip_data()

    def _load_ip_data(self):
        if self._should_generate_ip_data():
            print("Generating IP data...")
            ip_range = "0.0.0.0/0"
            generate_ip_data(ip_range, self.json_file)

        with open(self.json_file, "r") as f:
            self.ip_data = json.load(f)

    def _should_generate_ip_data(self):
        if not pathlib.Path(self.json_file).exists():
            return True

        modification_time = pathlib.Path(self.json_file).stat().st_mtime
        age_in_days = (time.time() - modification_time) / (60 * 60 * 24)

        return age_in_days > 30

    def get_random_ip(self):
        return random.choice(list(self.ip_data.keys()))

    def resolve(self, request, handler):
        reply = request.reply()
        q = request.q
        if q.qtype == QTYPE.A:
            logger.debug('Resolving IP address for query: %s', q.qname)
            start_time = time.time()
            ip = self.get_random_ip()
            elapsed_time = time.time() - start_time
            logger.debug(
                'Found random IP: %s (elapsed time: %.2f seconds)', ip, elapsed_time)
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
