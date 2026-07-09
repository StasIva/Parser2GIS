from __future__ import annotations

import random
import time
from typing import Any

import httpx


USER_AGENTS: list[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
]


class RateLimitExceeded(Exception):
    pass


class HttpClient:
    def __init__(self, delay_ms: int = 500, max_retries: int = 3,
                 timeout_seconds: int = 30, rotate_ua: bool = True) -> None:
        self._delay_ms = delay_ms
        self._max_retries = max_retries
        self._timeout = timeout_seconds
        self._rotate_ua = rotate_ua
        self._last_request: float = 0.0
        self._client = httpx.Client(timeout=httpx.Timeout(timeout_seconds), follow_redirects=True)

    @property
    def delay_ms(self) -> int:
        return self._delay_ms

    @delay_ms.setter
    def delay_ms(self, value: int) -> None:
        self._delay_ms = value

    def _get_user_agent(self) -> str:
        return random.choice(USER_AGENTS)

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {
            "Accept": "text/html,application/json,*/*",
            "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
        if self._rotate_ua:
            headers["User-Agent"] = self._get_user_agent()
        return headers

    def _rate_limit(self) -> None:
        elapsed = time.monotonic() - self._last_request
        min_interval = self._delay_ms / 1000.0
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self._last_request = time.monotonic()

    def get(self, url: str, params: dict[str, str] | None = None) -> httpx.Response:
        last_error: Exception | None = None
        for attempt in range(self._max_retries):
            try:
                self._rate_limit()
                response = self._client.get(url, headers=self._headers(), params=params)
                response.raise_for_status()
                return response
            except httpx.TimeoutException as e:
                last_error = e
                if attempt < self._max_retries - 1:
                    time.sleep(2 ** attempt)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    raise RateLimitExceeded("429 Too Many Requests")
                if e.response.status_code >= 500 and attempt < self._max_retries - 1:
                    last_error = e
                    time.sleep(2 ** attempt)
                    continue
                raise
            except httpx.RequestError as e:
                last_error = e
                if attempt < self._max_retries - 1:
                    time.sleep(2 ** attempt)
        raise httpx.RequestError(f"Request failed after {self._max_retries} retries") from last_error

    def post(self, url: str, json_data: dict[str, Any] | None = None) -> httpx.Response:
        last_error: Exception | None = None
        for attempt in range(self._max_retries):
            try:
                self._rate_limit()
                response = self._client.post(url, headers=self._headers(), json=json_data)
                response.raise_for_status()
                return response
            except httpx.TimeoutException as e:
                last_error = e
                if attempt < self._max_retries - 1:
                    time.sleep(2 ** attempt)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    raise RateLimitExceeded("429 Too Many Requests")
                if e.response.status_code >= 500 and attempt < self._max_retries - 1:
                    last_error = e
                    time.sleep(2 ** attempt)
                    continue
                raise
            except httpx.RequestError as e:
                last_error = e
                if attempt < self._max_retries - 1:
                    time.sleep(2 ** attempt)
        raise httpx.RequestError(f"Request failed after {self._max_retries} retries") from last_error

    def close(self) -> None:
        self._client.close()