# Taiwan Job Market Analysis - 專案結構

## 根目錄

```
Taiwan_Job_Market_Analysis/
├── .git/
├── .gitignore
├── TJMA.code-workspace
├── docker-compose.yml
├── ps.md
├── pyrightconfig.json
└── services/
    ├── upload/
    │   ├── __init__.py
    │   ├── dockerfile
    │   ├── pyproject.toml
    │   ├── ps.md
    │   ├── config/
    │   │   ├── __pycache__/
    │   │   │   └── config_log.cpython-312.pyc
    │   │   ├── config_log.py
    │   │   └── mysql_schema.py
    │   ├── logs/
    │   │   └── log
    │   └── src/
    │       ├── __init__.py
    │       ├── main.py
    │       ├── __pycache__/
    │       │   ├── __init__.cpython-312.pyc
    │       │   └── main.cpython-312.pyc
    │       ├── extractors/
    │       │   ├── __init__.py
    │       │   ├── crawler.py
    │       │   └── __pycache__/
    │       │       ├── __init__.cpython-312.pyc
    │       │       └── crawler.cpython-312.pyc
    │       ├── interfaces/
    │       │   ├── __init__.py
    │       │   ├── dtos.py
    │       │   ├── interfaces.py
    │       │   └── __pycache__/
    │       │       ├── __init__.cpython-312.pyc
    │       │       └── interfaces.cpython-312.pyc
    │       ├── loaders/
    │       │   ├── __init__.py
    │       │   ├── repo.py
    │       │   └── __pycache__/
    │       │       ├── __init__.cpython-312.pyc
    │       │       └── repo.cpython-312.pyc
    │       ├── transformers/
    │       │   ├── __init__.py
    │       │   ├── cleaner.py
    │       │   ├── test.py
    │       │   └── __pycache__/
    │       │       ├── __init__.cpython-312.pyc
    │       │       └── cleaner.cpython-312.pyc
    │       └── utils/
    │           └── (其他檔案...)
    └── web_server/
        └── (6個檔案)
```

## 統計資訊

- 總共發現 57+ 個檔案和目錄
- 主要服務：
  - `upload`: 資料上傳服務 (24 個項目)
  - `web_server`: 網頁伺服器 (6 個項目)

## 專案架構說明

這是一個 Taiwan Job Market Analysis 專案，採用微服務架構：

### Upload Service

包含完整的 ETL (Extract, Transform, Load) 流程：

- **extractors**: 爬蟲模組
- **transformers**: 資料清理與轉換模組
- **loaders**: 資料載入模組（資料庫操作）
- **interfaces**: 介面定義與 DTOs
- **config**: 設定檔（日誌、資料庫 schema）
- **utils**: 工具函式

### Web Server

提供網頁介面服務

### 配置檔案

- `docker-compose.yml`: Docker 容器編排
- `pyrightconfig.json`: Python 型別檢查設定
- `TJMA.code-workspace`: VS Code 工作區設定
