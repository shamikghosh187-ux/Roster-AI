import ipaddress
import socket
from urllib.parse import urlparse
from urllib.request import Request, urlopen


class Browser:
    """Minimal HTTP(S) reader with local-network target protection."""

    def _validate_target(self, url):
        u = urlparse(url)
        if u.scheme not in {"http", "https"} or not u.hostname:
            raise ValueError("only public HTTP(S) URLs are allowed")
        host = u.hostname.strip().lower().rstrip(".")
        if host == "localhost" or host.endswith(".localhost"):
            raise ValueError("local network targets are not allowed")
        try:
            addresses = {item[4][0] for item in socket.getaddrinfo(host, None)}
        except socket.gaierror as exc:
            raise ValueError(f"unable to resolve host: {host}") from exc
        for address in addresses:
            ip = ipaddress.ip_address(address)
            if (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_multicast
                or ip.is_unspecified
                or ip.is_reserved
            ):
                raise ValueError("local or reserved network targets are not allowed")
        return u

    def open(self, url, max_bytes=200000):
        if max_bytes <= 0:
            raise ValueError("max_bytes must be positive")
        self._validate_target(url)
        with urlopen(
            Request(url, headers={"User-Agent": "Roster-AI/1.0"}),
            timeout=10,
        ) as response:
            body = response.read(max_bytes).decode("utf-8", "ignore")
            return {
                "url": url,
                "content_type": response.headers.get("content-type", ""),
                "body": body,
            }
