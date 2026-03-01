"""設定模組 — 所有常數集中管理，不可變。"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class DBConfig:
    host: str = "localhost"
    port: int = 7535
    database: str = "postgres"
    user: str = "postgres"
    password: str = ""


@dataclass(frozen=True)
class APIConfig:
    token: str = ""
    start_date: str = "2015-01-01"
    end_date: str = "2026-02-26"
    # 免費方案：600 次/小時，間隔 6.5 秒留餘量
    request_interval: float = 6.5


@dataclass(frozen=True)
class RetryConfig:
    max_retries: int = 3
    base_delay: float = 10.0
    max_delay: float = 120.0


@dataclass(frozen=True)
class AppConfig:
    db: DBConfig = field(default_factory=DBConfig)
    api: APIConfig = field(default_factory=APIConfig)
    retry: RetryConfig = field(default_factory=RetryConfig)
    stock_list_csv: str = r"..\上市+上櫃公司證券代碼.csv"
