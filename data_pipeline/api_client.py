"""FinMind API 客戶端 — 限速 + 指數退避重試。"""
import logging
import time

import requests

from config import APIConfig, RetryConfig

logger = logging.getLogger(__name__)

FINMIND_URL = "https://api.finmindtrade.com/api/v4/data"
DATASET = "TaiwanStockMonthRevenue"


class RateLimiter:
    """固定間隔限速：每次請求前確保距上次至少 interval 秒。"""

    def __init__(self, interval: float) -> None:
        self._interval = interval
        self._last: float = 0.0

    def wait(self) -> None:
        elapsed = time.monotonic() - self._last
        if elapsed < self._interval:
            time.sleep(self._interval - elapsed)
        self._last = time.monotonic()


class FinMindClient:
    def __init__(self, api: APIConfig, retry: RetryConfig) -> None:
        self._api = api
        self._retry = retry
        self._limiter = RateLimiter(api.request_interval)
        self._session = requests.Session()

    def fetch_monthly_revenue(self, stock_id: str) -> list[dict]:
        """下載單支股票月營收，含限速與重試。"""
        params = {
            "dataset": DATASET,
            "data_id": stock_id,
            "start_date": self._api.start_date,
            "end_date": self._api.end_date,
        }
        if self._api.token:
            params["token"] = self._api.token

        for attempt in range(1, self._retry.max_retries + 1):
            self._limiter.wait()
            try:
                resp = self._session.get(FINMIND_URL, params=params, timeout=30)
                resp.raise_for_status()
                body = resp.json()
                if body.get("msg") != "success":
                    raise ValueError(f"API 錯誤: {body.get('msg')}")
                return body.get("data", [])
            except Exception as exc:
                delay = min(
                    self._retry.base_delay * (2 ** (attempt - 1)),
                    self._retry.max_delay,
                )
                logger.warning("[%s] 第 %d 次失敗: %s，%.0f 秒後重試", stock_id, attempt, exc, delay)
                if attempt == self._retry.max_retries:
                    raise
                time.sleep(delay)

        return []
