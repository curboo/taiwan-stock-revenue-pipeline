# 基於台股基本面資料擴展的公式化 Alpha 因子挖掘

**Formulaic Alpha Mining with Taiwan-Specific Fundamental Operator Extension In Equities**

> 劉宏昱 | AN4111013 | 115 學年度專題

---

## 研究摘要

台股擁有全球少見的月營收強制揭露制度（每月 10 日前公布），使投資人得以每月獲得企業經營資訊。本研究以**公式化 Alpha** 框架為基礎，將月營收、融券餘額、外資持股等台股特有基本面資料納入訊號設計，並透過**遺傳規劃演算法（GP）**自動搜索具有截面報酬預測力的新訊號公式。

## 專案結構

```
.
├── data_pipeline/      # 資料收集與清洗（FinMind API → PostgreSQL）
├── signals/            # 基本面與技術訊號設計
├── gp_search/          # 遺傳規劃搜索引擎
├── backtest/           # 回測框架
├── analysis/           # 多因子模型實證分析
└── notebooks/          # 探索性分析筆記
```

## 執行時程

| 週次 | 工作內容 | 狀態 |
|------|---------|------|
| 第 2~3 週 | 資料收集與清理（API 串接、歷史資料庫建立） | ✅ 完成 |
| 第 3~7 週 | 訊號設計（月營收、融券、外資持股） | ⏳ 待開始 |
| 第 4~14 週 | 遺傳規劃搜索 | ⏳ 待開始 |
| 第 9~16 週 | 實證分析（多因子模型回歸） | ⏳ 待開始 |
| 第 16~17 週 | 報告撰寫 | ⏳ 待開始 |

## 資料庫現況

<!-- AUTO-GENERATED -->
| 資料表 | 說明 | 範圍 |
|--------|------|------|
| `alpha_monthly_revenue` | 全市場月營收 | 2015-01 ~ 2026-02（231,257 筆）|
| `alpha_financial_statements` | 損益表（Income Statement） | 2018-01-01 ~ 2026-02-26 |
| `alpha_balance_sheet` | 資產負債表（Balance Sheet） | 2018-01-01 ~ 2026-02-26 |
| `alpha_cash_flows` | 現金流量表（Cash Flow Statement） | 2018-01-01 ~ 2026-02-26 |
| `alpha_download_progress` | 月營收下載進度 | 1,934 支（全數完成）|
| `alpha_financial_progress` | 財務三表下載進度 | 多維度追蹤（股票 × 資料集）|

有效股票（月營收≥ 81 筆）：**1,712 支**，清單見 `stock_list_81up.txt`。
<!-- AUTO-GENERATED -->

## 資料來源

- **FinMind** — 月營收、日成交資料（免費 API）
- **TEJ** — 融券餘額、外資持股比率
- **台灣證券交易所** — 上市/上櫃公司清單

## 關鍵字

`Alpha` `Momentum` `遺傳算法` `因子挖掘` `台股` `量化投資`
