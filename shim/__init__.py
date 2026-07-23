"""
Homelab assistant shim - collects local system state as a structured snapshot.
"""

import json
from typing import Optional

import httpx



def get_shim(url: str = "http://localhost:8765", indent: Optional[int] = None) -> str:
    try:
        response = httpx.get(f"{url}/state")
        response.raise_for_status()

        return json.dumps(response.json(), indent=indent, ensure_ascii=False)

    except httpx.HTTPError:
        return "Connection error!"
