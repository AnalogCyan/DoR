function between(x, min, max) {
  return x >= min && x <= max;
}

function indexCheck(ipAddress) {
  var XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;
  var url = ipAddress + "/index.html";
  var http = new XMLHttpRequest();
  http.open("HEAD", url, false);
  http.send();
  console.log(http.status);
  if (http.status != 0 && !between(http.status, 400, 499)) {
    console.log("file exists");
    return true;
  } else {
    console.log("file does not exist");
    return false;
  }
}

async function GenerateIPaddress() {
  while (true) {
    // Attempt to generate a random IP address.
    var out1 = Math.floor(Math.random() * (255 - 0 + 1));
    var out2 = Math.floor(Math.random() * (255 - 0 + 1));
    var out3 = Math.floor(Math.random() * (255 - 0 + 1));
    var out4 = Math.floor(Math.random() * (255 - 0 + 1));
    var address = out1 + "." + out2 + "." + out3 + "." + out4;

    // Validate the IP address; break on success.
    let tmp = await require("ping").promise.probe(address);
    if (require("net").isIPv4(address) && tmp.alive) {
      if (indexCheck("http://" + address) || indexCheck("https://" + address)) {
        break;
      }
    }

    // Log failures.
    console.log(
      require("net").isIPv4(address).toString() +
        " " +
        tmp.alive.toString() +
        " " +
        address
    );
  }

  return address;
}

async function main() {
  // Configure DNS server.
  const DnsServer = require("dns-host");
  const dnsServer = new DnsServer();

  // Generate IP on request.
  dnsServer.on("request", async (data) => {
    console.log("Data:", data);
    if (JSON.stringify(data).includes('"recordType":"A"')) {
      var rs = await GenerateIPaddress().then((values) => {
        return values;
      });
      console.log(rs);
      return rs;
    }
  });

  dnsServer.on("error", (err) => {
    console.log("An Error Occurred:", err);
  });

  dnsServer.on("start", () => {
    console.log("DNS server started");
  });

  dnsServer.on("stop", () => {
    console.log("DNS server stopped");
  });

  dnsServer.start();

  // This will stop the server.
  // dnsServer.stop();
}

main();

// 0, 404, 400
