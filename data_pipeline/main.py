"""主程式入口。"""
import logging
import os
import sys

from api_client import FinMindClient
from config import AppConfig, DBConfig, APIConfig
from db import Database
from downloader import Downloader
from stock_list import load_stock_ids


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("download.log", encoding="utf-8"),
        ],
    )


def main() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)

    # 從環境變數讀取敏感設定（不硬編碼在代碼中）
    db_cfg = DBConfig(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "7535")),
        database=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
    )
    api_cfg = APIConfig(
        token=os.getenv("FINMIND_TOKEN", ""),
    )
    config = AppConfig(db=db_cfg, api=api_cfg)

    # 1. 初始化資料庫
    db = Database(config.db)
    db.ensure_tables()

    # 2. 讀取股票清單
    stock_ids = load_stock_ids(config.stock_list_csv)

    # 3. 執行下載
    client = FinMindClient(config.api, config.retry)
    result = Downloader(db, client).run(stock_ids)

    # 4. 輸出結果
    logger.info(
        "完成！總計 %d | 本次成功 %d | 失敗 %d | 先前已完成 %d",
        result["total"], result["success"], result["failed"], result["already_done"],
    )
    if result["failed"] > 0:
        logger.warning("有 %d 支失敗，重新執行即可自動重試", result["failed"])


if __name__ == "__main__":
    main()
