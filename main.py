import logging
from pathlib import Path

import click

from config.config_log import set_up_logging
from services.cleaner import (
    make_job_skill_or_specialty,
    make_jobid_with_jobname_and_category,
    process_salary_info,
    use_original_documents_make_df,
)
from services.crawler import One_zero_four_crawler
from services.db import MongoDB_one_zero_four

set_up_logging(debug=False)
logger = logging.getLogger(__name__)


class JobDataPipeline:
    def __init__(self):
        # 有在猶豫無狀態是否還要弄成 class, 最終決定避免在一次任務中重複建立 instance
        self.crawler = One_zero_four_crawler()
        self.db = MongoDB_one_zero_four()

    def fetch_data_and_save_to_db(self, keyword: str, area: str):
        if not isinstance(keyword, str) and not isinstance(area, str):
            logger.error("Keyword and area must be strings.")
            return

        # 爬取資料
        try:
            logger.info(f"Start crawling data with keyword: {keyword} and area: {area}")
            datas = self.crawler.job_cleaned_pipeline_bronze(keyword, area)
        except Exception as e:
            logger.exception(f"Failed to crawl data: {e}")

        # 將資料存入資料庫
        try:
            self.db.insert_into_bronze(datas)
            logger.info(f"Use {keyword} to fetch data and save to db successfully")
        except Exception as e:
            logger.exception(f"Failed to connection to MongoDB:{e}")

    def select_bronze_data_and_output_csv(self, job_name_include_regex, file_title):
        """
        from bronze db select data and output csv files
        output csv files:
            1. job name with job id
            2. skill
            3. specialty
            4. exact salary
            5. negotiable salary
        """

        # 先檢查結果 path 是否存在, 不存在則創建, 使用 Path 物件操作是 gemini 教的
        # 放在第一個, 避免它在最後才出錯浪費資源
        result_dir = Path("result")
        result_dir.mkdir(parents=True, exist_ok=True)

        # 從資料庫取出資料, pattern: Data from bronze
        # 沒給條件表示全部取出, 因此給空 dict
        if not job_name_include_regex:
            condition = {}
            documents = self.db.select_from_bronze(condition)
        else:
            condition = {"header.jobName": {"$regex": job_name_include_regex, "$options": "i"}}
            documents = self.db.select_from_bronze(condition)

        if not documents:
            logger.error("No documents found in the database.")
            return

        logger.info(f"Fetched {len(documents)} documents. Starting transformation...")

        # 將資料轉換成 DF
        original_df = use_original_documents_make_df(documents)

        # job_name with job_id 作為映射主表
        input_dfs = {
            "job_name": make_jobid_with_jobname_and_category(original_df),
            "skills": make_job_skill_or_specialty(original_df, "skill"),
            "specialtys": make_job_skill_or_specialty(original_df, "specialty"),
            "exact_salary": process_salary_info(original_df, mode="exact"),
            "negotiable_salary": process_salary_info(original_df, mode="negotiable"),
        }

        logger.info(f"Exporting {len(input_dfs)} CSV files to {result_dir.absolute()}...")

        # 將資料輸出成 csv 格式, 以便 PowerBI 使用
        for name, df in input_dfs.items():
            file_path = result_dir / f"{file_title}_{name}.csv"
            try:
                df.to_csv(file_path, index=False, encoding="utf-8-sig")
            except Exception as e:
                logger.exception(f"Failed to export {name} to CSV: {e}")

        logger.info("Export to csv files completed.")


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
    ctx.obj["pipeline"] = JobDataPipeline()


@cli.command()
@click.option("-k", "--keyword", required=True, help="搜尋關鍵字")
@click.option("-a", "--area", default="台北市", show_default=True, help="搜尋地區")
@click.pass_context  # 2. 加上這個讓它能接收 ctx
def fetch(ctx, keyword, area):
    """僅執行資料爬取"""
    # 3. 直接從 ctx 拿出來用，不用再 pipeline = ...
    pipeline = ctx.obj["pipeline"]
    pipeline.fetch_data_and_save_to_db(keyword, area)


@cli.command()
@click.option("-r", "--regex", required=False, default=None, help="職缺名稱 Regex")
@click.option("-f", "--filename", required=True, help="輸出檔名")
@click.pass_context
def export(ctx, regex, filename):
    """僅執行匯出"""
    pipeline = ctx.obj["pipeline"]
    pipeline.select_bronze_data_and_output_csv(regex, filename)


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
    #         main.fetch_data_and_save_to_db(keyword, area)
