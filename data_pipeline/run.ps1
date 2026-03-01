# 執行月營收下載（在 Anaconda Prompt 中執行此腳本）
# 使用方式: .\run.ps1

$env:DB_HOST     = "localhost"
$env:DB_PORT     = "7535"
$env:DB_NAME     = "postgres"
$env:DB_USER     = "postgres"
$env:DB_PASSWORD = $env:DB_PASSWORD   # 從外部環境變數讀取，不在腳本中硬編碼
$env:FINMIND_TOKEN = $env:FINMIND_TOKEN

& "C:\Users\user\anaconda3\python.exe" main.py
