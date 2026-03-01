"""股票清單讀取模組。"""
import logging

logger = logging.getLogger(__name__)


def load_stock_ids(csv_path: str) -> list[str]:
    """
    解析 CSV 格式：'1101 台泥,,' → 取出 '1101'。
    第一行為標題，跳過。
    """
    stock_ids: list[str] = []
    with open(csv_path, encoding="utf-8-sig") as f:
        lines = f.readlines()

    for line in lines[1:]:
        cell = line.strip().split(",")[0].strip()
        if not cell:
            continue
        code = cell.split()[0]
        if code and (code.isdigit() or code.replace("-", "").isalnum()):
            stock_ids.append(code)

    logger.info("讀取到 %d 支股票代號", len(stock_ids))
    return stock_ids
