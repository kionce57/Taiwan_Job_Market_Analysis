import logging
from collections.abc import Iterator

import click
import pandas as pd

from config.config_log import set_up_logging
from config.mysql_schema import (
    bridge_category,
    bridge_language,
    bridge_major,
    bridge_skills,
    bridge_specialties,
    cust_info,
    dim_job,
    job_detail,
    metadata_obj,
    salary_type,
    welfare,
)
from src.interfaces.interfaces import BronzeJobRepository, SilverJobRepository
from src.extractors.crawler import Crawler, OneZeroFourCrawler
from src.loaders.repo import MongoDB_one_zero_four
from src.loaders.sql_repo import TjmaDatabase
from src.transformers.cleaner import (
    make_all_job_related_dfs,
    make_cust_df,
    make_dim_job,
    make_original_df,
)

set_up_logging(debug=False)
logger = logging.getLogger(__name__)

# 請使用這種路徑 uv run python -m src.main, 否則它導入 module 會失敗


class JobDataPipeline:
    BATCH_SIZE = 100

    def __init__(
        self,
        crawler: Crawler,
        bronze_repo: BronzeJobRepository,
        silver_repo: SilverJobRepository | None = None,
    ):
        # 有在猶豫無狀態是否還要弄成 class, 最終決定避免在一次任務中重複建立 instance
        self.crawler = crawler
        self.bronze_repo = bronze_repo
        self.silver_repo = silver_repo

    def fetch_data_and_save_to_repo(self, keyword: str, area: str):
        if not isinstance(keyword, str) and not isinstance(area, str):
            logger.error("Keyword and area must be strings.")
            return

        # 爬取資料
        try:
            logger.info(f"Start crawling data with keyword: {keyword} and area: {area}")
            datas: Iterator = self.crawler.harvest_jobs(keyword, area)
            buffer = []
            total_inserted = 0
            for data in datas:
                buffer.append(data)

                if len(buffer) >= self.BATCH_SIZE:
                    # 將資料存入資料庫
                    self._flush_buffer(buffer)
                    total_inserted += len(buffer)
                    buffer.clear()

            if buffer:  # 如果 buffer 還有剩餘的資料, 就再存一次
                self._flush_buffer(buffer)
                total_inserted += len(buffer)

            logger.info(f"Bronze pipeline completed. Total records inserted: {total_inserted}")
        except Exception as e:
            # 這裡可以做更細緻的錯誤處理，例如發送警報
            logger.exception(f"Pipeline failed during execution: {e}")

    def bronze_to_silver(self, job_name_regex: str | None = None) -> None:
        """
        bronze_to_silver 階段：
        1. 從 Bronze Repo (MongoDB) 取出資料
        2. 轉換為 Pandas DataFrame
        3. 將 cust_info 存入 Silver Repo (MySQL)
        4. 將 dim_job 存入 Silver Repo
        5. 從 Silver Repo 取回 job_id -> id 的映射
        6. 將其他 DataFrames 存入 Silver Repo
        """
        if self.silver_repo is None:
            raise ValueError("Silver repo (TjmaDatabase) is not initialized.")

        logger.info("Starting bronze_to_silver pipeline...")

        # Step 0: 確保表格存在 (使用正確的 schema)
        logger.info("Creating tables if not exist...")
        self.silver_repo.create_tables(metadata_obj)

        # Step 0.5: 插入 salary_type 參考資料
        logger.info("Inserting salary_type reference data...")
        salary_type_data = pd.DataFrame(
            [
                {"type": 10, "name": "面議"},
                {"type": 20, "name": "時薪"},
                {"type": 30, "name": "論件計酬"},
                {"type": 40, "name": "日薪"},
                {"type": 50, "name": "月薪"},
                {"type": 60, "name": "年薪"},
                {"type": 70, "name": "部分工時(月薪)"},
            ]
        )
        self.silver_repo.insert_stage(salary_type, salary_type_data)

        # Step 1: 從 Bronze Repo 取出資料
        logger.info("Fetching data from Bronze (MongoDB)...")
        documents = self.bronze_repo.select_stage(job_name_regex=job_name_regex)
        if not documents:
            logger.warning("No documents found in Bronze repo.")
            return

        logger.info(f"Fetched {len(documents)} documents from Bronze.")

        # Step 2: 轉換為原始 DataFrame
        original_df = make_original_df(documents)

        # Step 3: 製作並存入 cust_info
        logger.info("Processing and inserting cust_info...")
        cust_df = make_cust_df(original_df)
        self.silver_repo.insert_stage(cust_info, cust_df)
        logger.info(f"Inserted {len(cust_df)} records into cust_info.")

        # Step 4: 製作並存入 dim_job
        logger.info("Processing and inserting dim_job...")
        dim_job_df = make_dim_job(original_df)
        self.silver_repo.insert_stage(dim_job, dim_job_df)
        logger.info(f"Inserted {len(dim_job_df)} records into dim_job.")

        # Step 5: 從 Silver Repo 取回 job_id -> id 的映射
        logger.info("Fetching job_uid mapping from dim_job...")
        job_uid_df = self.silver_repo.select_stage(dim_job, columns=["id", "job_id"])
        logger.info(f"Retrieved {len(job_uid_df)} job_id mappings.")

        # Step 6: 製作所有依賴 job_uid 的 DataFrame
        logger.info("Processing job-related DataFrames...")
        all_dfs = make_all_job_related_dfs(original_df, job_uid_df)

        # Step 7: 存入各個表
        table_mapping = {
            "job_detail": job_detail,
            "welfare": welfare,
            "major": bridge_major,
            "skills": bridge_skills,
            "specialties": bridge_specialties,
            "category": bridge_category,
            "language": bridge_language,
        }

        for df_name, df in all_dfs.items():
            table = table_mapping[df_name]
            if not df.empty:
                logger.info(f"Inserting {len(df)} records into {table.name}...")
                self.silver_repo.insert_stage(table, df)
            else:
                logger.debug(f"Skipping {table.name} (empty DataFrame).")

        logger.info("bronze_to_silver pipeline completed successfully.")

    def _flush_buffer(self, data: list[dict]):
        """Helper method to write data to repo"""
        try:
            self.bronze_repo.insert_stage(data)
            logger.debug(f"Flushed batch of {len(data)} records to repo.")
        except Exception as e:
            logger.error(f"Failed to insert batch to repo: {e}")
            raise e  # 拋出異常以中止 Pipeline，或選擇記錄後繼續 (視業務需求)


# CLI 入口點
# cmd pattern: uv run python -m src.main --keyword "python" --area "6001001000" --mode "crawl"
# cmd pattern: uv run python -m src.main --mode "transform"
@click.command()
@click.option("--keyword", "-k", default="python", help="Search keyword for job listings")
@click.option("--area", "-a", default="6001001000", help="Area code for job search")
@click.option("--mode", "-m", type=click.Choice(["crawl", "transform"]), default="crawl")
@click.option("--regex", "-r", default=None, help="Job name regex for transform mode")
def main(keyword: str, area: str, mode: str, regex: str | None):
    """Taiwan Job Market Analysis - Data Pipeline"""
    if mode == "crawl":
        crawler = OneZeroFourCrawler()
        bronze_repo = MongoDB_one_zero_four()
        pipeline = JobDataPipeline(crawler, bronze_repo)
        pipeline.fetch_data_and_save_to_repo(keyword, area)
    elif mode == "transform":
        crawler = OneZeroFourCrawler()
        bronze_repo = MongoDB_one_zero_four()
        silver_repo = TjmaDatabase()
        pipeline = JobDataPipeline(crawler, bronze_repo, silver_repo)
        pipeline.bronze_to_silver(job_name_regex=regex)


if __name__ == "__main__":
    main()
