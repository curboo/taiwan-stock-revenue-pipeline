"""下載協調器 — 斷點續傳 + 進度追蹤 + 錯誤統計。"""
import logging
import time

from api_client import FinMindClient
from db import Database

logger = logging.getLogger(__name__)


class Downloader:
    def __init__(self, db: Database, client: FinMindClient) -> None:
        self._db = db
        self._client = client

    def run(self, all_stock_ids: list[str]) -> dict:
        """
        主流程：
        1. 初始化進度表
        2. 取得待下載清單（斷點續傳）
        3. 逐支下載 → 寫入 → 更新進度
        4. 回傳統計
        """
        self._db.init_progress(all_stock_ids)
        pending = self._db.get_pending_stocks()
        total = len(all_stock_ids)
        done_before = total - len(pending)

        logger.info("總計 %d 支，已完成 %d，待下載 %d", total, done_before, len(pending))

        success = failed = 0
        start = time.monotonic()

        for i, stock_id in enumerate(pending, 1):
            try:
                records = self._client.fetch_monthly_revenue(stock_id)
                count = self._db.upsert_revenues(records)
                self._db.mark_completed(stock_id, count)
                success += 1

                elapsed = time.monotonic() - start
                rate = i / elapsed * 3600 if elapsed > 0 else 0
                eta = (len(pending) - i) / (i / elapsed) if elapsed > 0 else 0
                logger.info(
                    "[%d/%d] %s 完成 (%d 筆) | 速率 %.0f 支/hr | ETA %.1f min",
                    done_before + i, total, stock_id, count, rate, eta / 60,
                )
            except Exception as exc:
                self._db.mark_failed(stock_id, str(exc))
                failed += 1
                logger.error("[%s] 失敗: %s", stock_id, exc)

        return {
            "total": total,
            "already_done": done_before,
            "success": success,
            "failed": failed,
        }
