# 專案資料夾結構

生成時間: 2025-12-16T13:52:42+08:00

## 目錄結構

```text
Taiwan_Job_Market_Analysis/services/crawler/
│
├── .env.example                    # 環境變數範例檔案
├── .python-version                 # Python 版本指定檔案
├── .ruff_cache/                    # Ruff linter 快取目錄
├── .venv/                          # Python 虛擬環境
│
├── .vscode/                        # VS Code 配置
│   ├── launch.json                 # 偵錯設定
│   └── settings.json               # 編輯器設定
│
├── config/                         # 配置檔案目錄
│   ├── __pycache__/
│   ├── config_log.py               # 日誌配置
│   └── mysql_schema.py             # MySQL 資料庫結構定義
│
├── logs/                           # 日誌檔案目錄
│
├── src/                            # 原始碼主目錄
│   ├── __init__.py
│   ├── __pycache__/
│   ├── main.py                     # 主程式進入點
│   │
│   ├── extractors/                 # 資料擷取模組
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   └── crawler.py              # 爬蟲程式
│   │
│   ├── interfaces/                 # 介面定義模組
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   ├── dtos.py                 # 資料傳輸物件
│   │   └── interfaces.py           # 介面定義
│   │
│   ├── loaders/                    # 資料載入模組
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   └── repo.py                 # 資料庫操作
│   │
│   ├── transformers/               # 資料轉換模組
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   ├── cleaner.py              # 資料清理程式
│   │   └── test.py                 # 測試檔案
│   │
│   └── utils/                      # 工具模組
│       └── area_category_for_transformer.json  # 地區分類資料
│
├── __init__.py
├── dockerfile                      # Docker 容器配置
├── ps.md                          # 專案結構說明文件 (本檔案)
├── pyproject.toml                 # Python 專案配置檔案
├── todo.md                        # 待辦事項清單
└── uv.lock                        # UV 套件管理器鎖定檔案
```

## 架構說明

### ETL 架構

本專案採用 ETL (Extract, Transform, Load) 架構:

1. **Extract (extractors/)** - 從 104 人力銀行爬取職缺資料
2. **Transform (transformers/)** - 清理和轉換資料格式
3. **Load (loaders/)** - 將處理後的資料載入 MySQL 資料庫

### 主要模組

- **extractors/crawler.py**: 實作網頁爬蟲邏輯
- **transformers/cleaner.py**: 資料清理與標準化
- **loaders/repo.py**: 資料庫連接與資料載入
- **interfaces/**: 定義各模組間的介面與資料結構
- **config/**: 系統配置,包含日誌和資料庫結構

## 技術棧

- Python 3.x
- MySQL 資料庫
- Docker 容器化
- UV 套件管理器
