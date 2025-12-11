# Taiwan Job Market Analysis

A comprehensive tool to analyze the job market in Taiwan by crawling data from the 104 Job Bank, storing it in a MongoDB database, and processing it for visualization.

## Features

- **Data Collection**: Crawl job details (skills, salary, requirements) from 104 Job Bank based on keywords and areas.
- **Data Storage**: Store raw and processed data in MongoDB Atlas (Bronze Layer).
- **Data Cleaning**: Classify job titles, normalize skills, and process salary information (monthly/annual conversion).
- **Data Export**: Export processed data to CSV files for visualization in tools like PowerBI.
- **CLI Interface**: Easy-to-use command-line interface for all operations.

## Tech Stack

- **Language**: Python 3.13+
- **Package Manager**: [uv](https://github.com/astral-sh/uv)
- **Database**: MongoDB Atlas
- **Libraries**:
  - `pandas`: Data manipulation
  - `pymongo`: MongoDB interaction
  - `requests`: HTTP requests
  - `click`: CLI creation

## Prerequisites

- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) installed
- MongoDB Atlas account and cluster

## Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd Taiwan_Job_Market_Analysis
   ```

2. **Install dependencies**

   ```bash
   uv sync
   ```

## Configuration

1. Create a `.env` file in the root directory.
2. Add your MongoDB Atlas credentials:

   ```env
   MONGO_HOST=your-cluster-url.mongodb.net
   CLUSTER=your-cluster-name
   DB_USER=your-username
   DB_PASSWORD=your-password
   ```

   > **Note**: Ensure your IP address is whitelisted in your MongoDB Atlas Network Access settings.

## Usage

Run the tool using `uv run python main.py`.

### 1. Fetch Data

Crawl job data and save it to the database.

```bash
uv run python main.py fetch -k "Python" -a "台北市"
```

- `-k`, `--keyword`: Search keyword (e.g., "Python", "Data Engineer").
- `-a`, `--area`: Search area (default: "台北市").

### 2. Export Data

Select data from the database and export it to CSV files in the `result/` directory.

```bash
uv run python main.py export -f "python_jobs" -r "Python"
```

- `-f`, `--filename`: Prefix for the output CSV files.
- `-r`, `--regex`: (Optional) Regex to filter job names.

### 3. Run All

Execute the complete workflow: Fetch -> Save -> Export.

```bash
uv run python main.py run_all -k "Data Scientist" -a "新北市" -f "ds_jobs"
```

## Project Structure

```text
.
├── config/             # Configuration files (logging)
|   └── config_log.py      # Configuration settings
├── services/           # Core logic
│   ├── crawler.py      # 104 Job Bank crawler
│   ├── db.py           # MongoDB operations
│   ├── cleaner.py      # Data cleaning and transformation
│   ├── LLM.py          # LLM integration
|   └── ...
├── main.py             # CLI entry point
├── pyproject.toml      # Project dependencies
└── README.md           # Project documentation
```

## Workflow

```mermaid
graph TD
    %% Styles
    classDef input fill:#f9f,stroke:#333,stroke-width:2px;
    classDef process fill:#e1f5fe,stroke:#0277bd,stroke-width:2px;
    classDef db fill:#fff3e0,stroke:#ff9800,stroke-width:2px,stroke-dasharray: 5 5;
    classDef chart fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;

    %% Module 1: Scraper
    subgraph Scraper_System [Scraper & Data Acquisition]
        A[User Input: Keyword & Area]:::input -->|Validate| B(Input Validation)
        B --> C{Convert to 104 Area Code}:::process
        C --> D[Fetch Job Detail URLs]:::process
        D --> E[Fetch Details & Basic Cleaning]:::process
    end

    %% Module 2: Bronze Layer
    E --> F[(MongoDB - Bronze Layer)]:::db

    %% Module 3: Data Pipeline
    subgraph Data_Pipeline [Data Processing Pipeline]
        F -->|Fetch Data| G[Transform to DataFrame]:::process
        G --> H[Clean & Structure Data]:::process
        H --> I[Export CSV Files]:::process
    end

    %% Module 4: Visualization
    subgraph Visualization [Visualization]
        I --> K[PowerBI / Analysis]:::chart
    end
```
