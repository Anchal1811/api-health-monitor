import requests
import ssl
import socket
from datetime import datetime
from urllib.parse import urlparse


def ping_endpoint(url: str) -> dict:
    result = {
        "url": url,
        "is_up": False,
        "status_code": None,
        "response_ms": None,
        "error_msg": None,
        "checked_at": datetime.utcnow(),
    }
    try:
        start = datetime.utcnow()
        response = requests.get(url, timeout=5, allow_redirects=True)
        end = datetime.utcnow()
        response_ms = (end - start).total_seconds() * 1000
        result["status_code"] = response.status_code
        result["response_ms"] = round(response_ms, 2)
        result["is_up"] = response.status_code < 500
    except requests.exceptions.Timeout:
        result["error_msg"] = "Request timed out (>5s)"
    except requests.exceptions.ConnectionError:
        result["error_msg"] = "Connection refused or DNS failure"
    except requests.exceptions.RequestException as e:
        result["error_msg"] = str(e)[:200]
    return result


def check_ssl_expiry(url: str) -> dict:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        return {"ssl": False, "days_remaining": None, "msg": "Not HTTPS"}
    try:
        hostname = parsed.hostname
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=hostname) as s:
            s.settimeout(5)
            s.connect((hostname, 443))
            cert = s.getpeercert()
            expiry_str = cert["notAfter"]
            expiry_date = datetime.strptime(expiry_str, "%b %d %H:%M:%S %Y %Z")
            days = (expiry_date - datetime.utcnow()).days
            return {
                "ssl": True,
                "days_remaining": days,
                "msg": f"Expires in {days} days" if days > 0 else "EXPIRED",
            }
    except Exception as e:
        return {"ssl": True, "days_remaining": None, "msg": f"SSL check failed: {str(e)[:100]}"}