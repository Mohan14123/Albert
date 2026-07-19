"""Shared OAuth 2.0 helpers — real HTTP calls via httpx."""

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class OAuthHelper:
    """Reusable helpers for the Authorization Code flow."""

    @staticmethod
    def build_redirect_url(
        base_url: str,
        client_id: str,
        scopes: list[str],
        redirect_uri: str,
        state: str,
    ) -> str:
        """Build a standards-compliant OAuth 2.0 authorization URL."""
        from urllib.parse import urlencode

        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(scopes),
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
        return f"{base_url}?{urlencode(params)}"

    @staticmethod
    async def exchange_code(
        token_url: str,
        client_id: str,
        client_secret: str,
        code: str,
        redirect_uri: str,
    ) -> dict[str, Any]:
        """Exchange an authorization code for access + refresh tokens."""
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                token_url,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
                headers={"Accept": "application/json"},
            )
        response.raise_for_status()
        return response.json()

    @staticmethod
    async def refresh_token(
        token_url: str,
        client_id: str,
        client_secret: str,
        refresh_token: str,
    ) -> dict[str, Any]:
        """Use a refresh token to obtain a fresh access token."""
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                token_url,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
                headers={"Accept": "application/json"},
            )
        response.raise_for_status()
        return response.json()
