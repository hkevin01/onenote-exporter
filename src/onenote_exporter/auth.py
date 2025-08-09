"""Authentication helpers using MSAL device code flow."""
from __future__ import annotations

import pathlib

import msal

from .config import AUTHORITY, CLIENT_ID, SCOPES, TOKEN_CACHE_PATH


def acquire_token() -> str:
    """Acquire an access token using MSAL's device code flow.

    Returns:
        str: Bearer token string
    """
    cache = msal.SerializableTokenCache()
    if TOKEN_CACHE_PATH and pathlib.Path(TOKEN_CACHE_PATH).exists():
        try:
            cache.deserialize(
                pathlib.Path(TOKEN_CACHE_PATH).read_text(encoding="utf-8")
            )
        except (OSError, ValueError):
            # Ignore cache read errors
            pass

    app = msal.PublicClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        token_cache=cache,
    )

    # Attempt silent acquisition first
    accounts = app.get_accounts()
    result = (
        app.acquire_token_silent(scopes=SCOPES, account=accounts[0])
        if accounts
        else None
    )

    if not result:
        flow = app.initiate_device_flow(scopes=SCOPES)
        if "user_code" not in flow:
            raise RuntimeError(
                "Failed to create device flow. Check app registration and "
                "scopes."
            )
        print("To sign in, visit and enter the code:")
        print(flow["verification_uri"])
        print("Code:", flow["user_code"])
        result = app.acquire_token_by_device_flow(flow)

    if "access_token" not in result:
        raise RuntimeError(
            "Failed to acquire token: "
            f"{result.get('error_description') or result}"
        )

    # Persist cache
    if TOKEN_CACHE_PATH:
        path = pathlib.Path(TOKEN_CACHE_PATH)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(cache.serialize(), encoding="utf-8")

    return result["access_token"]
