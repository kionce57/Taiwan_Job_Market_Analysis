import logging
from pathlib import Path

from services.cleaner import (
    make_job_skill_or_specialty,
    make_jobid_with_jobname,
    process_salary_info,
    use_original_documents_make_df,
)
from services.config_log import set_up_logging
from services.crawler import One_zero_four_crawler
from services.db import MongoDB_one_zero_four

set_up_logging(debug=False)
logger = logging.getLogger(__name__)


class JobDataPipeline:
    def __init__(self):
        # 有在猶豫是否要弄成 class, 最終決定避免在一次任務中需要重複建立其他功能 class
        self.crawler = One_zero_four_crawler()
        self.db = MongoDB_one_zero_four()

    def fetch_data_and_save_to_db(self, keyword: str, area: str):
        if not isinstance(keyword, str) and not isinstance(area, str):
            logger.error("Keyword and area must be strings.")
            return

        try:
            # 爬取資料
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
            "job_name": make_jobid_with_jobname(original_df),
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

    # def main():
    # 用 argument 讓 user 控制程序的行為 [fetch and save | select and draw | fetch and save, and then select and draw]


if __name__ == "__main__":
    main = JobDataPipeline()
    # next kw: 
    # keyword = 
    # area = "台北市"
    # main.fetch_data_and_save_to_db(keyword, area)

    job_name_include_regex = r"Python|Software Engineer|資料工程|Backend"
    file_title = "python_taipei"
    main.select_bronze_data_and_output_csv(job_name_include_regex, file_title)
