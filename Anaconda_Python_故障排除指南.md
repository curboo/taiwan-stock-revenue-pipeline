# Anaconda Python 執行故障排除指南

## 問題現象

當在 PowerShell 中執行 Python 腳本時，出現以下情況：
- ✗ `python script.py` 命令失敗或無輸出
- ✗ Python 找不到已安裝的套件
- ✗ 執行的是錯誤的 Python 版本（非 Anaconda）

## 根本原因

您使用 **Anaconda** 管理 Python 環境，但當前 PowerShell 終端機並未初始化 Anaconda 環境，導致：
1. 系統找到的是 Windows Store 版本的 Python
2. 無法使用 `conda` 命令
3. 缺少 Anaconda 環境中已安裝的套件

---

## 解決方案

### 方法一：使用完整 Python 路徑（推薦用於一次性執行）

#### 步驟 1：找到 Anaconda 安裝位置

```powershell
# 檢查常見安裝位置
Test-Path "C:\Users\user\Anaconda3\python.exe"
Test-Path "C:\Users\user\anaconda3\python.exe"
Test-Path "C:\ProgramData\Anaconda3\python.exe"

# 或者搜尋 Anaconda 目錄
Get-ChildItem "C:\Users\user" -Directory -Filter "*conda*" -ErrorAction SilentlyContinue
```

#### 步驟 2：使用完整路徑執行腳本

```powershell
# 假設找到的路徑是 C:\Users\user\anaconda3\python.exe
C:\Users\user\anaconda3\python.exe your_script.py --arg1 value1 --arg2 value2
```

**實際範例**：
```powershell
C:\Users\user\anaconda3\python.exe "Alpha Label Analyzer.py" --data training_data_2330_alpha158_2022-01-01_2025-11-10.parquet --output ./output_2330
```

---

### 方法二：初始化 Anaconda 環境（推薦用於長期使用）

#### 步驟 1：初始化 Conda

```powershell
# 找到 conda 初始化腳本
& "C:\Users\user\anaconda3\Scripts\conda.exe" init powershell
```

#### 步驟 2：重新啟動 PowerShell

關閉並重新打開 PowerShell 終端機，此時應該會看到 `(base)` 提示符。

#### 步驟 3：正常執行腳本

```powershell
python your_script.py --arg1 value1
```

---

### 方法三：使用 Anaconda Prompt（最簡單）

1. 按 `Win` 鍵搜尋 **"Anaconda Prompt"**
2. 打開後，Conda 環境已自動啟用
3. 切換到工作目錄：
   ```powershell
   cd "C:\Users\user\Desktop\量化交易模組\特徵工程"
   ```
4. 執行腳本：
   ```powershell
   python "Alpha Label Analyzer.py" --data training_data.parquet --output ./output
   ```

---

## 診斷工具命令

### 檢查當前 Python 版本來源

```powershell
# 查看 Python 可執行檔位置
where.exe python

# 預期看到 Anaconda 路徑，例如：
# C:\Users\user\anaconda3\python.exe

# 如果看到以下路徑則表示使用了錯誤的 Python：
# C:\Users\user\AppData\Local\Microsoft\WindowsApps\python.exe  ❌ (Windows Store 版本)
```

### 檢查 Conda 是否可用

```powershell
conda --version
# 如果顯示 "conda : The term 'conda' is not recognized..."
# 表示環境未初始化，需使用方法一或方法二
```

### 查看已安裝的 Python 套件

```powershell
# 使用完整路徑檢查套件
C:\Users\user\anaconda3\python.exe -m pip list

# 或在 Conda 環境中
conda list
```

---

## 常見問題 Q&A

### Q1: 為什麼不能直接使用 `python` 命令？

**A**: Windows 系統有多個 Python 安裝源（Anaconda、官方安裝包、Windows Store），系統會按照 PATH 環境變數順序選擇第一個。如果 Anaconda 未加入 PATH 或排序較後，就會使用錯誤的版本。

### Q2: 使用完整路徑會不會很麻煩？

**A**: 對於自動化腳本或臨時測試，使用完整路徑反而更可靠，避免環境變數污染問題。如果經常使用，建議初始化 Conda 環境（方法二）。

### Q3: 如何切換不同的 Conda 虛擬環境？

**A**: 
```powershell
# 查看所有環境
conda env list

# 切換到指定環境
conda activate your_env_name

# 回到 base 環境
conda activate base
```

---

## 完整執行流程範例

```powershell
# 1. 確認 Anaconda Python 路徑
Test-Path "C:\Users\user\anaconda3\python.exe"  # 應返回 True

# 2. 切換到工作目錄
cd "C:\Users\user\Desktop\量化交易模組\特徵工程"

# 3. 使用完整路徑執行腳本
C:\Users\user\anaconda3\python.exe "Alpha Label Analyzer.py" `
  --data training_data_2330_alpha158_2022-01-01_2025-11-10.parquet `
  --output ./output_2330

# 4. 檢查輸出結果
explorer.exe ./output_2330
```

---

## 總結

| 方法 | 適用場景 | 優點 | 缺點 |
|------|---------|------|------|
| **完整路徑** | 一次性執行、自動化腳本 | 可靠、無需配置 | 路徑較長 |
| **初始化 Conda** | 長期開發使用 | 使用便利 | 需配置環境 |
| **Anaconda Prompt** | 快速測試 | 零配置 | 需另開視窗 |

> 💡 **建議**: 對於 AI 助手執行命令，使用**方法一（完整路徑）**最為可靠且不需要使用者手動配置環境。
