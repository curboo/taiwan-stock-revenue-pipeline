# Data Pipeline — 資料收集模組

從 FinMind API 下載台股月營收資料，存入本地 PostgreSQL。

## 快速開始

```bash
# 1. 安裝依賴
pip install -r requirements.txt

# 2. 設定環境變數（參考 ../.env.example）
set DB_PASSWORD=your_password
set FINMIND_TOKEN=your_token   # 免費帳號可不設定，但有速率差異

# 3. 執行下載（支援斷點續傳）
cd data_pipeline
python main.py
```

## 模組說明

| 檔案 | 職責 |
|------|------|
| `config.py` | 所有常數（DB 連線、API 參數、限速設定），不可變 dataclass |
| `db.py` | PostgreSQL 操作（建表、upsert、進度追蹤） |
| `api_client.py` | FinMind HTTP API 封裝（固定間隔限速 + 指數退避重試）|
| `stock_list.py` | 解析上市+上櫃股票代號 CSV |
| `downloader.py` | 下載協調器（斷點續傳、進度顯示、錯誤統計）|
| `main.py` | 程式入口，從環境變數組裝設定 |

## 環境變數

<!-- AUTO-GENERATED from .env.example + config.py -->
| 變數 | 必填 | 預設值 | 說明 |
|------|------|--------|------|
| `DB_HOST` | 否 | `localhost` | PostgreSQL 主機 |
| `DB_PORT` | 否 | `7535` | PostgreSQL 連接埠 |
| `DB_NAME` | 否 | `postgres` | 資料庫名稱 |
| `DB_USER` | 否 | `postgres` | 資料庫使用者 |
| `DB_PASSWORD` | **是** | —— | 資料庫密碼（勿寫入程式碼）|
| `FINMIND_TOKEN` | 否 | `""` | FinMind API Token（免費方案 600 次/小時）|
<!-- AUTO-GENERATED -->

## 限速策略

<!-- AUTO-GENERATED from config.py -->
| 參數 | 值 |
|------|----|
| 請求間隔 | 6.5 秒（留 10% 餘量）|
| 免費方案上限 | 600 次/小時 |
| 全市場下載時間 | ~3.5 小時（1,934 支）|
| 重試次數 | 最多 3 次，指數退避（10s → 20s → 120s）|
<!-- AUTO-GENERATED -->

## 資料庫 Schema

```sql
-- 月營收資料（主表）
alpha_monthly_revenue (
    stock_id      VARCHAR(10),   -- 股票代號
    date          DATE,          -- 報告月份（每月 1 日）
    revenue       BIGINT,        -- 當月營收（元）
    revenue_month INTEGER,       -- 報告月份（數字）
    revenue_year  INTEGER,       -- 報告年份
    fetched_at    TIMESTAMPTZ,
    PRIMARY KEY (stock_id, date)
)

-- 下載進度追蹤
alpha_download_progress (
    stock_id      VARCHAR(10) PRIMARY KEY,
    status        VARCHAR(20),   -- pending | completed | failed
    records_count INTEGER,
    error_msg     TEXT,
    updated_at    TIMESTAMPTZ
)
```

## 現況（截至 2026-03-02）

<!-- AUTO-GENERATED -->
- 下載完成：**1,934 / 1,934 支**（失敗 0）
- 總筆數：**231,257 筆**
- 日期範圍：`2015-01-01` ~ `2026-02-01`
- 有效股票（≥ 81 筆）：**1,712 支** → `../stock_list_81up.txt`
<!-- AUTO-GENERATED -->
