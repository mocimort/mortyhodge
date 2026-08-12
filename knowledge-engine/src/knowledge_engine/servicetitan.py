"""ServiceTitan API client — read-only export of completed jobs.

Auth: OAuth2 client-credentials against auth.servicetitan.io, then every API
call carries the bearer token plus the ST-App-Key header. Docs:
https://developer.servicetitan.io/
"""
from __future__ import annotations

import time
from typing import Any, Iterator

import httpx

from .config import settings

AUTH_URL = "https://auth.servicetitan.io/connect/token"
API_BASE = "https://api.servicetitan.io"


class ServiceTitanClient:
    def __init__(self) -> None:
        self._token: str | None = None
        self._token_expiry: float = 0.0
        self._http = httpx.Client(timeout=30)

    def _get_token(self) -> str:
        if self._token and time.time() < self._token_expiry - 60:
            return self._token
        resp = self._http.post(
            AUTH_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": settings.st_client_id,
                "client_secret": settings.st_client_secret,
            },
        )
        resp.raise_for_status()
        payload = resp.json()
        self._token = payload["access_token"]
        self._token_expiry = time.time() + payload.get("expires_in", 900)
        return self._token

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self._http.get(
            f"{API_BASE}{path}",
            params=params or {},
            headers={
                "Authorization": f"Bearer {self._get_token()}",
                "ST-App-Key": settings.st_app_key,
            },
        )
        resp.raise_for_status()
        return resp.json()

    # --- exports -----------------------------------------------------------

    def completed_jobs(self, limit: int = 50) -> Iterator[dict[str, Any]]:
        """Yield completed jobs, newest first, up to `limit`."""
        tenant = settings.st_tenant_id
        page = 1
        fetched = 0
        while fetched < limit:
            data = self._get(
                f"/jpm/v2/tenant/{tenant}/jobs",
                params={
                    "jobStatus": "Completed",
                    "sort": "-completedOn",
                    "page": page,
                    "pageSize": min(50, limit - fetched),
                },
            )
            items = data.get("data", [])
            if not items:
                return
            for job in items:
                yield job
                fetched += 1
                if fetched >= limit:
                    return
            if not data.get("hasMore"):
                return
            page += 1

    def job_notes(self, job_id: int) -> list[dict[str, Any]]:
        tenant = settings.st_tenant_id
        data = self._get(f"/jpm/v2/tenant/{tenant}/jobs/{job_id}/notes")
        return data.get("data", [])
