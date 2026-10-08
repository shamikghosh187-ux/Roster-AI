import ipaddress
import socket
from urllib.error import HTTPError
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


class _NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Browser:
    """Minimal HTTP(S) reader with local-network target protection."""

    @staticmethod
    def _validate_target(url):
        u = urlparse(url)
        if u.scheme not in {"http", "https"} or not u.hostname:
            raise ValueError("only public HTTP(S) URLs are allowed")
        if u.username is not None or u.password is not None:
            raise ValueError("URLs with embedded credentials are not allowed")
        host = u.hostname.strip().lower().rstrip(".")
        if host == "localhost" or host.endswith(".localhost"):
            raise ValueError("local network targets are not allowed")
        try:
            port = u.port
        except ValueError as exc:
            raise ValueError("invalid URL port") from exc
        if port is not None and not 1 <= port <= 65535:
            raise ValueError("invalid URL port")
        return u

    @staticmethod
    def _resolve_public(host):
        try:
            addresses = socket.getaddrinfo(host, None)
        except socket.gaierror as exc:
            raise ValueError(f"unable to resolve host: {host}") from exc
        for address in {item[4][0] for item in addresses}:
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

    def open(self, url, max_bytes=200000, max_redirects=5):
        if not isinstance(max_bytes, int) or isinstance(max_bytes, bool) or max_bytes <= 0:
            raise ValueError("max_bytes must be a positive integer")
        if not isinstance(max_redirects, int) or isinstance(max_redirects, bool) or max_redirects < 0:
            raise ValueError("max_redirects must be a non-negative integer")
        opener = build_opener(_NoRedirectHandler, ProxyHandler({}))
        current = url
        for _ in range(max_redirects + 1):
            parsed = self._validate_target(current)
            self._resolve_public(parsed.hostname.strip().lower().rstrip("."))
            try:
                with opener.open(
                    Request(current, headers={"User-Agent": "Roster-AI/1.0"}),
                    timeout=10,
                ) as response:
                    body = response.read(max_bytes).decode("utf-8", "ignore")
                    return {
                        "url": current,
                        "content_type": response.headers.get("content-type", ""),
                        "body": body,
                    }
            except HTTPError as exc:
                if exc.code not in {301, 302, 303, 307, 308}:
                    raise
                location = exc.headers.get("Location")
                if not location:
                    raise ValueError("redirect response has no location") from exc
                current = urljoin(current, location)
        raise ValueError("too many redirects")
