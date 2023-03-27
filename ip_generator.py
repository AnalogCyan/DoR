import json
import os
from ping3 import ping
import requests
from ipaddress import IPv4Network


def ping_ip(ip, count=4):
    success = 0
    for _ in range(count):
        if ping(ip, timeout=1) is not None:
            success += 1
    return success / count


def check_html_page(ip):
    try:
        response = requests.get(f"http://{ip}", timeout=5)
        return response.status_code == 200 and "text/html" in response.headers["Content-Type"]
    except:
        return False


def save_to_json(ip, response_rate, json_file):
    data = {}
    if os.path.exists(json_file):
        with open(json_file, "r") as f:
            data = json.load(f)

    data[ip] = response_rate

    with open(json_file, "w") as f:
        json.dump(data, f, indent=4)


def main(ip_range, json_file):
    for ip in IPv4Network(ip_range).hosts():
        ip_str = str(ip)
        print(f"Processing {ip_str}")
        response_rate = ping_ip(ip_str)

        if response_rate > 0.75 and check_html_page(ip_str):
            save_to_json(ip_str, response_rate, json_file)


if __name__ == "__main__":
    ip_range = "0.0.0.0/0"
    json_file = "ip_data.json"
    main(ip_range, json_file)
