"""資料庫模組 — Schema 建立、upsert、進度追蹤。"""
import logging
from contextlib import contextmanager
from typing import Generator

import psycopg2
from psycopg2.extras import execute_values

from config import DBConfig

logger = logging.getLogger(__name__)

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS monthly_revenue (
    stock_id        VARCHAR(10)  NOT NULL,
    date            DATE         NOT NULL,
    revenue         BIGINT,
    revenue_month   INTEGER,
    revenue_year    INTEGER,
    fetched_at      TIMESTAMPTZ  DEFAULT NOW(),
    PRIMARY KEY (stock_id, date)
);
CREATE INDEX IF NOT EXISTS idx_mr_stock ON monthly_revenue (stock_id);
CREATE INDEX IF NOT EXISTS idx_mr_date  ON monthly_revenue (date);

CREATE TABLE IF NOT EXISTS download_progress (
    stock_id      VARCHAR(10) PRIMARY KEY,
    status        VARCHAR(20) NOT NULL DEFAULT 'pending',
    records_count INTEGER DEFAULT 0,
    error_msg     TEXT,
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);
"""


class Database:
    def __init__(self, config: DBConfig) -> None:
        self._cfg = config

    @contextmanager
    def _conn(self) -> Generator:
        conn = psycopg2.connect(
            host=self._cfg.host,
            port=self._cfg.port,
            dbname=self._cfg.database,
            user=self._cfg.user,
            password=self._cfg.password,
        )
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def ensure_tables(self) -> None:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(CREATE_TABLES_SQL)
        logger.info("資料庫 Schema 已就緒")

    def init_progress(self, stock_ids: list[str]) -> None:
        """批次初始化進度（已存在的跳過）。"""
        rows = [(sid,) for sid in stock_ids]
        sql = "INSERT INTO download_progress (stock_id) VALUES %s ON CONFLICT DO NOTHING"
        with self._conn() as conn:
            with conn.cursor() as cur:
                execute_values(cur, sql, rows)

    def get_pending_stocks(self) -> list[str]:
        """取得尚未完成的股票清單（斷點續傳核心）。"""
        sql = "SELECT stock_id FROM download_progress WHERE status != 'completed' ORDER BY stock_id"
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                return [row[0] for row in cur.fetchall()]

    def upsert_revenues(self, records: list[dict]) -> int:
        """批次寫入月營收，回傳寫入筆數。"""
        if not records:
            return 0
        rows = [
            (
                r.get("stock_id"),
                r.get("date"),
                r.get("revenue"),
                r.get("revenue_month"),
                r.get("revenue_year"),
            )
            for r in records
        ]
        sql = """
            INSERT INTO monthly_revenue (stock_id, date, revenue, revenue_month, revenue_year)
            VALUES %s
            ON CONFLICT (stock_id, date) DO UPDATE SET
                revenue       = EXCLUDED.revenue,
                revenue_month = EXCLUDED.revenue_month,
                revenue_year  = EXCLUDED.revenue_year,
                fetched_at    = NOW()
        """
        with self._conn() as conn:
            with conn.cursor() as cur:
                execute_values(cur, sql, rows)
                return cur.rowcount

    def mark_completed(self, stock_id: str, count: int) -> None:
        sql = """
            UPDATE download_progress
            SET status = 'completed', records_count = %s, updated_at = NOW()
            WHERE stock_id = %s
        """
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (count, stock_id))

    def mark_failed(self, stock_id: str, error: str) -> None:
        sql = """
            UPDATE download_progress
            SET status = 'failed', error_msg = %s, updated_at = NOW()
            WHERE stock_id = %s
        """
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (error[:500], stock_id))

    def get_summary(self) -> dict:
        sql = "SELECT status, COUNT(*) FROM download_progress GROUP BY status"
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                return {row[0]: row[1] for row in cur.fetchall()}
