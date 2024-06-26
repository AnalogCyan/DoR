# 🔗 DNS-over-RNG

DNS-over-RNG (DoR) is a parody project inspired by the various DNS-over-`protocol` standards. This unique DNS server utilizes the Shodan API to function, returning random IP addresses of operational web servers, allowing users to land on random websites with each DNS request. Intended for fun and entertainment, DoR provides an unconventional browsing experience.

The server employs a local cache mechanism to efficiently manage API requests, reducing the frequency of fetching data and adhering to API rate limits. While updated for greater efficiency, it is still not recommended for use as your primary DNS server. Embrace the chaos but proceed with caution. >:3

## Features

- Utilizes the Shodan API to retrieve IP addresses of servers in the US with port 80 open that serve HTML content.
- Maintains a local cache of these addresses, refreshing the data if older than 30 days or if the cache does not exist.
- Returns random, operational IP addresses from the cache, ensuring an unpredictable browsing experience.
- Improved efficiency through caching, reducing unnecessary API calls and speeding up response times.

## Live Instances

I was planning on hosting a live instance of the DNS-over-RNG server for demonstration, but have run into some issues doing so. If anyone knows the best way to host something like this, please let me know!

If anyone spins up their own public instance, please feel free to submit a pull request adding it to the list of instances below.

DNS Servers:

- `placeholder-data`

Please note that live instances are also not intended for production use and should only be used for testing and entertainment.

## How It Works

Upon receiving a DNS query, the DoR server processes the request and randomly selects a validated IP address from its local cache. This cache is populated using data from the Shodan API and is refreshed every 30 days to maintain currency and functionality.

## Installation and Usage

There are multiple ways you can set up and run DNS over RNG. You can run it directly with Python or use Docker for easier setup and deployment.

### Running Directly with Python

1. **Set the Shodan API Key:**
   Ensure the `SHODAN_API_KEY` environment variable is set to your Shodan API key. You can set it temporarily by running the following command:

```bash
export SHODAN_API_KEY=your_shodan_api_key_here
```

2. **Install Python and Dependencies:**
   Ensure you have Python 3.x installed along with the required packages. You can install the required packages using `pip`:

```bash
pip install -r requirements.txt
```

3. **Run the Server:**
   Run the server using the following command:

```bash
python server.py
```

4. **Configure Your DNS:**

   Configure your system or router to use your host machine’s IP as the DNS server.

### Running with Docker

For convenience, the project can also be run using Docker, which simplifies the deployment and ensures consistency across different platforms.

1. **Prepare the Environment File:**

   - Create a `.env` file in the same directory as your `docker compose.yml`.
   - Add the Shodan API key to the `.env` file with the following line:
     ```
     SHODAN_API_KEY=your_shodan_api_key_here
     ```
   - Ensure that you replace `your_shodan_api_key_here` with your actual Shodan API key.

2. **Pull the Docker Image:**

   - To pull the Docker container from Docker Hub, run:
     ```bash
     docker pull analogcyan/dns-over-rng:latest
     ```
   - Alternatively, you can build the image locally with:
     ```bash
     docker compose build
     ```

3. **Use Docker Compose:**

   - Start the server using Docker Compose with the following command:
     ```bash
     docker compose up
     ```
   - This command utilizes the `docker compose.yml` file which reads your `.env` file, setting the `SHODAN_API_KEY` environment successfully.

4. **Configure Your DNS:**
   - Configure your system or router to use your host machine’s IP as the DNS server.

### Note on DNS Configuration

- When configuring your system to use the DNS server, input the IP address of the Docker host if you are running the server via Docker.
- Ensure port 53 is open and listening to both TCP and UDP traffic on your firewall settings depending on your hosting environment.

## Warning

This server is designed for experimental and entertainment purposes and should not be used as a primary DNS service. By using the server, you acknowledge the potential for unexpected and random browsing results.

Enjoy the unpredictability and have fun exploring random corners of the web!
