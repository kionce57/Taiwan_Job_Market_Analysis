import logging
from collections.abc import Iterator
from pathlib import Path

import click

from config.config_log import set_up_logging
from src.extractors.crawler import Crawler, OneZeroFourCrawler
from src.loaders.repo import JobRepository, MongoDB_one_zero_four
from src.transformers.cleaner import (
    make_job_skill_or_specialty,
    make_jobid_with_jobname_and_category,
    process_salary_info,
    use_original_documents_make_df,
)

set_up_logging(debug=False)
logger = logging.getLogger(__name__)

# 請使用這種路徑 uv run python -m src.main, 否則它導入 module 會失敗


class JobDataPipeline:
    BATCH_SIZE = 100

    def __init__(self, crawler: Crawler, repo: JobRepository):
        # 有在猶豫無狀態是否還要弄成 class, 最終決定避免在一次任務中重複建立 instance
        self.crawler = crawler
        self.repo = repo

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

    def select_stage_and_output_csv(
        self, file_title: str, job_name_regex: str | None = None
    ) -> None:
        """
        ETL Export 階段：
        從 Bronze Repo 取出資料 -> 轉 Pandas DF -> 輸出 CSV
        """
        result_dir = Path("result")
        result_dir.mkdir(parents=True, exist_ok=True)

        try:
            # [優化] 直接傳遞參數，無論是 None 還是字串，交由 Repo 內部處理
            documents = self.repo.select_stage(job_name_regex)

            if not documents:
                logger.warning("No documents found in the database matching criteria.")
                return

            logger.info(f"Fetched {len(documents)} documents. Starting transformation...")

            # Transformation
            original_df = use_original_documents_make_df(documents)
            input_dfs = self._make_input_dfs(original_df)

            logger.info(f"Exporting {len(input_dfs)} CSV files to {result_dir.absolute()}...")

            # Export
            for name, df in input_dfs.items():
                file_path = result_dir / f"{file_title}_{name}.csv"
                df.to_csv(file_path, index=False, encoding="utf-8-sig")

            logger.info("Export to csv files completed.")

        except Exception as e:
            logger.exception(f"Failed to export CSVs: {e}")

    def _flush_buffer(self, data: list[dict]):
        """Helper method to write data to repo"""
        try:
            self.repo.insert_stage(data)
            logger.debug(f"Flushed batch of {len(data)} records to repo.")
        except Exception as e:
            logger.error(f"Failed to insert batch to repo: {e}")
            raise e  # 拋出異常以中止 Pipeline，或選擇記錄後繼續 (視業務需求)

    def _make_input_dfs(self, original_df) -> dict:
        input_dfs = {
            "job_name": make_jobid_with_jobname_and_category(original_df),
            "skills": make_job_skill_or_specialty(original_df, "skill"),
            "specialtys": make_job_skill_or_specialty(original_df, "specialty"),
            "exact_salary": process_salary_info(original_df, mode="exact"),
            "negotiable_salary": process_salary_info(original_df, mode="negotiable"),
        }
        return input_dfs


@click.group()
@click.pass_context
def cli(ctx):
    """
    Job Data Pipeline CLI 工具
    在這裡統一初始化 Class
    """
    # 確保 ctx.obj 是一個字典 (或直接存 pipeline 實例也可以)
    ctx.ensure_object(dict)

    # 1. 在這裡初始化一次，所有子指令都能用
    # 這樣就很有「放在一起」的感覺，邏輯也更集中
    ctx.obj["pipeline"] = JobDataPipeline(
        crawler=OneZeroFourCrawler(), repo=MongoDB_one_zero_four()
    )


@cli.command()
@click.option("-k", "--keyword", required=True, help="搜尋關鍵字")
@click.option("-a", "--area", default="台北市", show_default=True, help="搜尋地區")
@click.pass_context  # 2. 加上這個讓它能接收 ctx
def fetch(ctx, keyword, area):
    """僅執行資料爬取"""
    # 3. 直接從 ctx 拿出來用，不用再 pipeline = ...
    pipeline = ctx.obj["pipeline"]
    pipeline.fetch_data_and_save_to_repo(keyword, area)


@cli.command()
@click.option("-r", "--regex", required=False, default=None, help="職缺名稱 Regex")
@click.option("-f", "--filename", required=True, help="輸出檔名")
@click.pass_context
def export(ctx, regex, filename):
    """僅執行匯出"""
    pipeline = ctx.obj["pipeline"]
    pipeline.select_stage_and_output_csv(regex, filename)


@cli.command()
@click.option("-k", "--keyword", required=True)
@click.option("-a", "--area", default="台北市")
@click.option("-r", "--regex", required=False, default=None, help="職缺名稱 Regex")
@click.option("-f", "--filename", required=True)
@click.pass_context
def run_all(ctx, keyword, area, regex, filename):
    """執行完整流程"""
    # 使用 context invoke 可以直接呼叫上面的指令，避免重複代碼
    ctx.invoke(fetch, keyword=keyword, area=area)

    if regex is None:
        regex = keyword

    ctx.invoke(export, regex=regex, filename=filename)


if __name__ == "__main__":
    # example: uv run python main.py run_all -k 資料工程 -a 新北市 -r "Python|資料工程" -f "python_"
    # select regex: all
    cli()

    # if need...
    # import json
    # keywords = ["something", "something2",...,...]

    # with open("/services/area_category_for_transformer.json", "w", encoding="utf-8") as f:
    #     doc = json.load(f)
    #     areas = doc.keys()

    # for area in areas:
    #     for keyword in keywords:
    #         main = JobDataPipeline()
    #         main.fetch_data_and_save_to_repo(keyword, area)
