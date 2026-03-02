# Data Pipeline — 資料收集模組

從 FinMind API 下載台股月營收與財務報表資料，存入本地 PostgreSQL。

## 快速開始

### 月營收資料（Monthly Revenue）

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

### 財務報表（Financial Statements）

```bash
# 下載損益表、資產負債表、現金流量表
cd data_pipeline
python financial_main.py
```

或直接使用執行腳本（帶認證）：
```bash
python run_financial.py
```

## 模組說明

### 核心模組

| 檔案 | 職責 |
|------|------|
| `config.py` | 所有常數（DB 連線、API 參數、限速設定），不可變 dataclass |
| `db.py` | PostgreSQL 操作（建表、upsert、進度追蹤） |
| `api_client.py` | FinMind HTTP API 封裝（固定間隔限速 + 指數退避重試）|
| `stock_list.py` | 解析上市+上櫃股票代號 CSV |

### 月營收下載

| 檔案 | 職責 |
|------|------|
| `downloader.py` | 下載協調器（斷點續傳、進度顯示、錯誤統計）|
| `main.py` | 程式入口，從環境變數組裝設定 |
| `run_download.py` | 執行腳本（帶認證） |

### 財務報表下載

| 檔案 | 職責 |
|------|------|
| `financial_main.py` | 財務三表主程式（損益表、資產負債表、現金流量表） |
| `run_financial.py` | 執行腳本（帶認證，.gitignored） |

## 環境變數

<!-- AUTO-GENERATED from .env.example + config.py -->

### 資料庫設定

| 變數 | 必填 | 預設值 | 說明 |
|------|------|--------|------|
| `DB_HOST` | 否 | `localhost` | PostgreSQL 主機 |
| `DB_PORT` | 否 | `7535` | PostgreSQL 連接埠 |
| `DB_NAME` | 否 | `postgres` | 資料庫名稱 |
| `DB_USER` | 否 | `postgres` | 資料庫使用者 |
| `DB_PASSWORD` | **是** | —— | 資料庫密碼（勿寫入程式碼）|

### API 設定

| 變數 | 必填 | 預設值 | 說明 |
|------|------|--------|------|
| `FINMIND_TOKEN` | 否 | `""` | FinMind API Token（免費方案 600 次/小時，提供 token 後提速）|

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

### 月營收資料

```sql
-- 月營收（主表）
CREATE TABLE alpha_monthly_revenue (
    stock_id      VARCHAR(10)  NOT NULL,
    date          DATE         NOT NULL,
    revenue       BIGINT,
    revenue_month INTEGER,
    revenue_year  INTEGER,
    fetched_at    TIMESTAMPTZ  DEFAULT NOW(),
    PRIMARY KEY (stock_id, date)
);

CREATE INDEX idx_amr_stock ON alpha_monthly_revenue (stock_id);
CREATE INDEX idx_amr_date  ON alpha_monthly_revenue (date);

-- 月營收下載進度追蹤
CREATE TABLE alpha_download_progress (
    stock_id      VARCHAR(10) PRIMARY KEY,
    status        VARCHAR(20)  NOT NULL DEFAULT 'pending',
    records_count INTEGER      DEFAULT 0,
    error_msg     TEXT,
    updated_at    TIMESTAMPTZ  DEFAULT NOW()
);
```

### 財務三表資料

```sql
-- 損益表（Income Statement）
CREATE TABLE alpha_financial_statements (
    stock_id     VARCHAR(10)  NOT NULL,
    date         DATE         NOT NULL,
    type         VARCHAR(100) NOT NULL,
    value        NUMERIC,
    origin_name  VARCHAR(200),
    fetched_at   TIMESTAMPTZ  DEFAULT NOW(),
    PRIMARY KEY (stock_id, date, type)
);

CREATE INDEX idx_alpha_financial_statements_stock
    ON alpha_financial_statements (stock_id);

-- 資產負債表（Balance Sheet）
CREATE TABLE alpha_balance_sheet (
    stock_id     VARCHAR(10)  NOT NULL,
    date         DATE         NOT NULL,
    type         VARCHAR(100) NOT NULL,
    value        NUMERIC,
    origin_name  VARCHAR(200),
    fetched_at   TIMESTAMPTZ  DEFAULT NOW(),
    PRIMARY KEY (stock_id, date, type)
);

CREATE INDEX idx_alpha_balance_sheet_stock
    ON alpha_balance_sheet (stock_id);

-- 現金流量表（Cash Flow Statement）
CREATE TABLE alpha_cash_flows (
    stock_id     VARCHAR(10)  NOT NULL,
    date         DATE         NOT NULL,
    type         VARCHAR(100) NOT NULL,
    value        NUMERIC,
    origin_name  VARCHAR(200),
    fetched_at   TIMESTAMPTZ  DEFAULT NOW(),
    PRIMARY KEY (stock_id, date, type)
);

CREATE INDEX idx_alpha_cash_flows_stock
    ON alpha_cash_flows (stock_id);

-- 財務三表下載進度追蹤
CREATE TABLE alpha_financial_progress (
    stock_id      VARCHAR(10)  NOT NULL,
    dataset       VARCHAR(60)  NOT NULL,
    status        VARCHAR(20)  NOT NULL DEFAULT 'pending',
    records_count INTEGER      DEFAULT 0,
    error_msg     TEXT,
    updated_at    TIMESTAMPTZ  DEFAULT NOW(),
    PRIMARY KEY (stock_id, dataset)
);
```

## 現況（截至 2026-03-02）

<!-- AUTO-GENERATED -->

### 月營收資料

- 下載進度：**1,934 / 1,934 支**（完成率 100%）
- 總筆數：**231,257 筆**
- 日期範圍：2015-01-01 ~ 2026-02-01
- 有效股票（≥ 81 筆）：**1,712 支** → `../stock_list_81up.txt`

### 財務報表資料

- 支援資料集：
  - `TaiwanStockFinancialStatements` - 損益表
  - `TaiwanStockBalanceSheet` - 資產負債表
  - `TaiwanStockCashFlowsStatement` - 現金流量表
- 日期範圍：2018-01-01 ~ 2026-02-26
- 進度追蹤：多維度（股票 × 資料集）

<!-- AUTO-GENERATED -->

## 財務三表 API 說明

### 支援的資料集

| 資料集代碼 | 中文名稱 | 表名 | 說明 |
|----------|---------|------|------|
| `TaiwanStockFinancialStatements` | 損益表 | `alpha_financial_statements` | 營收、成本、淨利等 |
| `TaiwanStockBalanceSheet` | 資產負債表 | `alpha_balance_sheet` | 資產、負債、股東權益 |
| `TaiwanStockCashFlowsStatement` | 現金流量表 | `alpha_cash_flows` | 營運、投資、融資現金流 |

### 資料欄位

各財務三表資料的共同欄位結構：

```python
{
    "stock_id": "2330",          # 股票代號
    "date": "2025-12-31",        # 報告日期（通常為季末或年末）
    "type": "Revenue",           # 財務科目（損益表中為營收、成本等）
    "value": 1234567890,         # 數值（通常為元）
    "origin_name": "營業收入"    # 原始科目名稱
}
```

### 使用範例

#### Python 直接呼叫

```python
from api_client import FinMindClient
from config import APIConfig, RetryConfig

api_cfg = APIConfig(token="your_token")
retry_cfg = RetryConfig()
client = FinMindClient(api_cfg, retry_cfg)

# 下載特定股票的損益表
records = client.fetch_financial_data("TaiwanStockFinancialStatements", "2330")
for record in records:
    print(f"{record['date']} - {record['type']}: {record['value']}")
```

#### 批次下載（透過 financial_main.py）

```bash
cd data_pipeline
python financial_main.py
# 依序下載：損益表 → 資產負債表 → 現金流量表
# 支援斷點續傳
```

### 進度追蹤

財務三表下載進度儲存於 `alpha_financial_progress` 表：

- **多維度追蹤**：按（股票ID × 資料集）追蹤進度
- **狀態欄位**：`pending` → `completed`（或 `failed`）
- **錯誤捕捉**：各股票的失敗訊息保存於 `error_msg`
- **支援重試**：下次執行時自動跳過已完成的股票

### 設定參數

在 `config.py` 中：

```python
APIConfig:
    financial_start_date: str = "2018-01-01"  # 財務三表的起始日期
    end_date: str = "2026-02-26"               # 結束日期
    request_interval: float = 6.5              # 請求間隔（秒）
```

### 限速與重試策略

- **固定間隔限速**：6.5 秒間隔（留 10% 餘量給 FinMind 免費方案 600 次/小時）
- **指數退避重試**：失敗時重試，延遲時間依次為 10s → 20s → 120s（最多 3 次）
- **預估下載時間**：全市場財務三表約 **10.5 小時**（1,934 支 × 3 資料集）

## 工作流程

### 月營收下載流程

```
main.py
  ↓
load_stock_ids() → 解析股票代號
  ↓
downloader.py
  ├─ init_progress() → 初始化進度表
  ├─ get_pending_stocks() → 取得待下載清單
  └─ 迴圈：
    ├─ fetch_monthly_revenue() → 調用 API
    ├─ upsert_revenues() → 寫入資料庫
    └─ mark_completed() → 更新進度
```

### 財務三表下載流程

```
financial_main.py
  ↓
對於每個資料集（損益表、資產負債表、現金流量表）：
  ├─ init_financial_progress() → 初始化進度表
  ├─ get_pending_financial() → 取得待下載清單
  └─ 迴圈：
    ├─ fetch_financial_data() → 調用 API
    ├─ upsert_financial_data() → 寫入資料庫
    └─ mark_financial_completed() → 更新進度
```
