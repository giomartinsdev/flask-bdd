import json
from typing import Any

from flask.testing import FlaskClient


class BDDClient:
    def __init__(self, client: FlaskClient):
        self._client = client

    # ── Read ───────────────────────────────────────────────────────────────────

    def get(self, path: str, **kwargs):
        return self._client.get(path, **kwargs)

    def get_json(self, path: str, **kwargs) -> Any:
        """GET and return the parsed JSON body directly (skips the response object)."""
        return json.loads(self._client.get(path, **kwargs).data)

    # ── Write ──────────────────────────────────────────────────────────────────

    def json_post(self, path: str, body: dict):
        return self._client.post(
            path, data=json.dumps(body), content_type="application/json"
        )

    def json_put(self, path: str, body: dict):
        return self._client.put(
            path, data=json.dumps(body), content_type="application/json"
        )

    def json_patch(self, path: str, body: dict):
        return self._client.patch(
            path, data=json.dumps(body), content_type="application/json"
        )

    # ── Delete ─────────────────────────────────────────────────────────────────

    def delete(self, path: str):
        return self._client.delete(path)

    def json_delete(self, path: str, body: dict):
        """DELETE with a JSON body (for APIs that accept a payload on DELETE)."""
        return self._client.delete(
            path, data=json.dumps(body), content_type="application/json"
        )
