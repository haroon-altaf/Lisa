from __future__ import annotations

import random

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .template_logger import TemplateLogger

TIMEOUT = 10
MAX_RETRIES = 3
BACKOFF_FACTOR = 1.0
SESSION_RENEWAL_INTERVAL = 1000
UA_LIST = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
)

logger = TemplateLogger(__name__).logger


class WebSession:
    """
    Class to implement the resquests.get() method with automatic retries, headers, and session renewal (to avoid being blocked by sites).
    It is designed to be used as a context manager.
    """

    def __init__(
        self,
        timeout: int = TIMEOUT,
        max_retries: int = MAX_RETRIES,
        backoff_factor: float = BACKOFF_FACTOR,
        session_renewal_interval: int = SESSION_RENEWAL_INTERVAL,
        ua_list: tuple[str] = UA_LIST,
    ) -> None:
        self._timeout = timeout
        self._session_renewal_interval = session_renewal_interval
        self._ua_list = ua_list
        self._retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
        )
        self._session = self._init_session()
        self._success_count = 0

    def _init_session(self) -> requests.Session:
        session = requests.Session()
        adapter = HTTPAdapter(max_retries=self._retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update(
            {
                "User-Agent": random.choice(self._ua_list),
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Connection": "keep-alive",
            }
        )
        return session

    def get(self, url: str) -> requests.Response | None:
        try:
            response = self._session.get(url, timeout=self._timeout)
        except (requests.exceptions.RequestException, requests.exceptions.Timeout):
            logger.exception(f"GET request failed for: {url}")
            return None

        if not response.ok:
            logger.error(f"GET request failed for: {url}\nResponse code: {response.status_code}")
            return None

        self._success_count += 1
        current_count = self._success_count
        if current_count % self._session_renewal_interval == 0:
            self._session.close()
            self._session = self._init_session()
        return response

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()
