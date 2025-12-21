# Taiwan_Job_Market_Analysis 專案資料夾結構

```
Taiwan_Job_Market_Analysis/
├── .env.example
├── .git/
├── .gitignore
├── TJMA.code-workspace
├── docker-compose.yml
├── pyrightconfig.json
├── ps.md
│
├── backend/
│   ├── .venv/
│   ├── src/
│   └── uv.lock
│
├── init/
│   ├── init_users.sh
│   └── mysql_init.sh
│
└── services/
    ├── crawler/
    │   ├── .dockerignore
    │   ├── .env.example
    │   ├── .python-version
    │   ├── .ruff_cache/
    │   ├── .venv/
    │   ├── .vscode/
    │   │   ├── launch.json
    │   │   └── settings.json
    │   ├── __init__.py
    │   ├── config/
    │   │   ├── __pycache__/
    │   │   ├── config_log.py
    │   │   └── mysql_schema.py
    │   ├── dockerfile
    │   ├── logs/
    │   ├── ps.md
    │   ├── pyproject.toml
    │   ├── requirements.txt
    │   ├── todo.md
    │   ├── uv.lock
    │   └── src/
    │       ├── .env
    │       ├── __init__.py
    │       ├── __pycache__/
    │       ├── main.py
    │       ├── pattern.json
    │       ├── extractors/
    │       │   ├── __init__.py
    │       │   ├── __pycache__/
    │       │   └── crawler.py
    │       ├── interfaces/
    │       │   ├── __init__.py
    │       │   ├── __pycache__/
    │       │   ├── dtos.py
    │       │   └── interfaces.py
    │       ├── loaders/
    │       │   ├── __init__.py
    │       │   ├── __pycache__/
    │       │   ├── repo.py
    │       │   └── sql_repo.py
    │       ├── transformers/
    │       │   ├── __init__.py
    │       │   ├── __pycache__/
    │       │   ├── cleaner.py
    │       │   └── test.py
    │       └── utils/
    │           └── area_category_for_transformer.json
    │
    └── web_server/
        ├── .dockerignore
        ├── .env.example
        ├── .pytest_cache/
        ├── .python-version
        ├── .venv/
        ├── .vscode/
        │   ├── launch.json
        │   └── settings.json
        ├── Dockerfile
        ├── all.md
        ├── config/
        │   ├── __pycache__/
        │   ├── config_log.py
        │   └── mysql_schema.py
        ├── logs/
        ├── main.py
        ├── pyproject.toml
        ├── src/
        ├── tests/
        │   └── __pycache__/
        └── uv.lock
```

---

_Generated on: 2025-12-21_
