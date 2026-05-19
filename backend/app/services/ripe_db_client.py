from app.services.ripe_stat_client import RipeStatClient


class RipeDbClient:
    def __init__(self, client: RipeStatClient):
        self.client = client

    def whois(self, resource: str) -> dict:
        return self.client.get("whois", {"resource": resource})
