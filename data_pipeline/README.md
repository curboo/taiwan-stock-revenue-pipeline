# Data Pipeline — 資料收集模組

從 FinMind API 下載台股月營收資料，儲存至本地 PostgreSQL。

## 快速開始

```bash
# 安裝依賴
pip install -r requirements.txt

# 設定環境變數（避免密碼硬編碼）
export DB_PASSWORD=your_password
export FINMIND_TOKEN=your_token   # 免費帳號可不設定

# 初始化資料庫並開始下載
python main.py
```

## 模組說明

| 檔案 | 職責 |
|------|------|
| `config.py` | 設定常數（DB 連線、API 參數、限速設定） |
| `db.py` | PostgreSQL 操作（建表、upsert、進度追蹤） |
| `api_client.py` | FinMind API 封裝（限速 + 重試） |
| `stock_list.py` | 讀取上市+上櫃股票代號 CSV |
| `downloader.py` | 下載協調器（斷點續傳） |
| `main.py` | 程式進入點 |

## 限速策略

FinMind 免費 API 限制：**600 次/小時**

- 每次請求間隔 ≥ 6.5 秒（留 10% 餘量）
- 約 1934 支股票，全程約 **3.5 小時**
- 支援中斷後繼續（斷點續傳）

## 資料庫 Schema

```sql
-- 月營收資料
monthly_revenue (stock_id, date, revenue, revenue_month, revenue_year)
  PRIMARY KEY (stock_id, date)

-- 下載進度追蹤
download_progress (stock_id, status, records_count, error_msg)
  status: pending | completed | failed
```
