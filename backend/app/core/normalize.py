import ipaddress
import re


_ASN_RE = re.compile(r"^(?:AS)?(\d+)$", re.IGNORECASE)


def normalize_asn(value: str) -> int:
    m = _ASN_RE.match(value.strip())
    if not m:
        raise ValueError("Invalid ASN format")
    asn = int(m.group(1))
    if asn <= 0:
        raise ValueError("ASN must be > 0")
    return asn


def format_asn(value: int) -> str:
    if value <= 0:
        raise ValueError("ASN must be > 0")
    return f"AS{value}"


def validate_prefix(value: str) -> str:
    try:
        return str(ipaddress.ip_network(value.strip(), strict=False))
    except ValueError as exc:
        raise ValueError("Invalid prefix") from exc
