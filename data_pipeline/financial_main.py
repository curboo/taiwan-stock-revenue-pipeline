"""財務三表下載主程式（損益表 / 資產負債表 / 現金流量表）。"""
import logging
import os
import sys
import time

from api_client import FinMindClient, FINANCIAL_DATASETS
from config import AppConfig, DBConfig, APIConfig
from db import Database, DATASET_TABLE_MAP
from stock_list import load_stock_ids

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("financial_download.log", encoding="utf-8"),
        ],
    )


def download_dataset(
    db: Database,
    client: FinMindClient,
    dataset: str,
    stock_ids: list[str],
) -> dict:
    table = DATASET_TABLE_MAP[dataset]
    db.init_financial_progress(stock_ids, dataset)
    pending = db.get_pending_financial(dataset)
    total = len(stock_ids)
    done_before = total - len(pending)

    logger.info("[%s] 總計 %d 支，已完成 %d，待下載 %d", dataset, total, done_before, len(pending))

    success = failed = 0
    start = time.monotonic()

    for i, stock_id in enumerate(pending, 1):
        try:
            records = client.fetch_financial_data(dataset, stock_id)
            count = db.upsert_financial_data(table, records)
            db.mark_financial_completed(stock_id, dataset, count)
            success += 1

            elapsed = time.monotonic() - start
            rate = i / elapsed * 3600 if elapsed > 0 else 0
            eta = (len(pending) - i) / (i / elapsed) if elapsed > 0 else 0
            logger.info(
                "[%d/%d] %s | %-32s 完成 (%d 筆) | %.0f 支/hr | ETA %.1f min",
                done_before + i, total, stock_id, dataset, count, rate, eta / 60,
            )
        except Exception as exc:
            db.mark_financial_failed(stock_id, dataset, str(exc))
            failed += 1
            logger.error("[%s/%s] 失敗: %s", stock_id, dataset, exc)

    return {"total": total, "already_done": done_before, "success": success, "failed": failed}


def main() -> None:
    setup_logging()

    db_cfg = DBConfig(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "7535")),
        database=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
    )
    api_cfg = APIConfig(token=os.getenv("FINMIND_TOKEN", ""))
    config = AppConfig(db=db_cfg, api=api_cfg)

    db = Database(config.db)
    db.ensure_tables()  # 建立財務三表（若不存在）

    stock_ids = load_stock_ids(config.stock_list_csv)
    client = FinMindClient(config.api, config.retry)

    for dataset in FINANCIAL_DATASETS:
        result = download_dataset(db, client, dataset, stock_ids)
        logger.info(
            "[%s] 完成！成功 %d | 失敗 %d | 先前已完成 %d",
            dataset, result["success"], result["failed"], result["already_done"],
        )


if __name__ == "__main__":
    main()
