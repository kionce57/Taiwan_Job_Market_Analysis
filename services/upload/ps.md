# 專案資料夾結構

```
Taiwan_Job_Market_Analysis/services/upload/
├── .env.example                          # 環境變數範例檔案
├── .python-version                       # Python 版本設定
├── .venv/                                # 虛擬環境目錄
├── .vscode/                              # VS Code 設定目錄
│   └── settings.json                     # VS Code 專案設定
├── __init__.py                           # Python 套件初始化檔案
├── config/                               # 配置檔案目錄
│   ├── config_log.py                     # 日誌配置
│   └── mysql_schema.py                   # MySQL 資料庫結構定義
├── dockerfile                            # Docker 容器配置檔案
├── ps.md                                 # 專案結構文檔 (本檔案)
├── pyproject.toml                        # Python 專案配置與依賴管理
├── src/                                  # 原始碼目錄
│   ├── __init__.py                       # 套件初始化
│   ├── extractors/                       # 資料擷取器模組
│   │   ├── __init__.py
│   │   └── crawler.py                    # 網頁爬蟲實作
│   ├── interfaces/                       # 介面定義模組
│   │   ├── __init__.py
│   │   ├── dtos.py                       # 資料傳輸物件
│   │   └── interfaces.py                 # 介面定義
│   ├── loaders/                          # 資料載入器模組
│   │   ├── __init__.py
│   │   └── repo.py                       # 資料庫存取實作
│   ├── main.py                           # 主程式進入點
│   ├── transformers/                     # 資料轉換器模組
│   │   ├── __init__.py
│   │   ├── cleaner.py                    # 資料清理實作
│   │   └── test.py                       # 測試檔案
│   └── utils/                            # 工具函式模組
│       └── area_category_for_transformer.json  # 地區分類對照表
├── todo.md                               # 待辦事項清單
└── uv.lock                               # UV 套件管理器鎖定檔案
```

## 專案架構說明

### 核心目錄結構

- **config/**: 存放配置檔案

  - 日誌系統配置
  - 資料庫結構定義

- **src/**: 主要原始碼目錄，採用 ETL (Extract-Transform-Load) 架構
  - **extractors/**: 負責資料擷取
  - **transformers/**: 負責資料轉換與清理
  - **loaders/**: 負責資料載入至資料庫
  - **interfaces/**: 定義資料介面與 DTO
  - **utils/**: 輔助工具與資源檔案

### 配置檔案

- `.python-version`: 指定 Python 版本
- `pyproject.toml`: 專案依賴與配置
- `uv.lock`: UV 套件管理器的依賴鎖定
- `dockerfile`: Docker 容器化配置

### 文檔檔案

- `ps.md`: 專案結構文檔 (本檔案)
- `todo.md`: 專案待辦事項
- `.env.example`: 環境變數範例

---

_最後更新: 2025-12-16_
