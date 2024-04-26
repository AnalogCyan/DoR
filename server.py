import json
import logging
import os
import pathlib
import random
import socket
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

import requests
from dnslib import DNSRecord, RR, A, QTYPE
from dnslib.server import DNSServer, BaseResolver

import shodan


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Get Shodan API key from the env variable SHODAN_API_KEY
SHODAN_API_KEY = os.environ.get("SHODAN_API_KEY", None)
if not SHODAN_API_KEY:
    raise ValueError("SHODAN_API_KEY environment variable not set.")
api = shodan.Shodan(SHODAN_API_KEY)


class RandomIPResolver(BaseResolver):
    """
    A resolver class that randomly selects an IP address from a provided API that
    meets specific criteria - an operational HTTP server (port 80 open) in the US
    serving HTML content.
    """

    cache_file = "./cache/ip_cache.json"
    cache_duration = timedelta(days=30)

    def __init__(self):
        self.cache = None
        self.load_or_refresh_cache()

    def load_or_refresh_cache(self):
        """Loads the IP cache from disk or refreshes it if older than 30 days."""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r", encoding="utf-8") as f:
                self.cache = json.load(f)
            self.cache_date = datetime.strptime(self.cache["date"], "%Y-%m-%d")
            if datetime.now() - self.cache_date > self.cache_duration:
                self.refresh_cache()
        else:
            self.refresh_cache()

    def refresh_cache(self):
        """Fetches new data from the Shodan API and updates the cache."""
        results = api.search("port:80 country:US")
        self.cache = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "ips": [result["ip_str"] for result in results["matches"]],
        }
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(self.cache, f)

    def get_random_ip(self):
        """Retrieves a random IP from the cache, verifying it serves HTML content."""
        if not hasattr(self, "cache"):
            self.load_or_refresh_cache()

        ips = self.cache["ips"]
        while True:
            ip = random.choice(ips)
            if self.check_html_page(ip):
                return ip

    def check_html_page(self, ip):
        """Checks if the IP address hosts a valid HTML page."""
        try:
            response = requests.get(f"http://{ip}", timeout=5)
            return response.status_code == 200 and "text/html" in response.headers.get(
                "Content-Type", ""
            )
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return False

    def resolve(self, request, handler):
        """Processes and responds to DNS requests using cached IP addresses."""
        reply = request.reply()
        q = request.q
        if q.qtype == QTYPE.A:
            logger.debug("Resolving IP address for query: %s", q.qname)
            start_time = time.time()
            ip = self.get_random_ip()
            elapsed_time = time.time() - start_time
            logger.debug(
                "Found random IP: %s (elapsed time: %.2f seconds)", ip, elapsed_time
            )
            reply.add_answer(RR(rname=q.qname, rtype=QTYPE.A, rdata=A(ip), ttl=60))
        return reply


def main():
    """
    Runs the main application to instantiate a random IP DNS resolver and start a DNS server.

    This function sets up a DNS server using a `RandomIPResolver` to resolve queries for IP addresses
    to random, but valid and HTML-serving, addresses. It listens on port 53 and binds to all available
    IP addresses on the host machine. The DNS server is started, and it runs until interrupted by the
    user (e.g., via a KeyboardInterrupt).

    Upon starting, it logs that the DNS server is running. If a KeyboardInterrupt is received (usually
    triggered by pressing Ctrl+C), it logs that the DNS server is shutting down, calls the resolver's
    shutdown method to clean up any resources, and stops the DNS server.
    """
    resolver = RandomIPResolver()
    server = DNSServer(resolver, port=53, address="0.0.0.0")
    logger.info("Starting DNS server...")

    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("Shutting down DNS server...")
        resolver.shutdown()
        server.stop()


if __name__ == "__main__":
    main()
