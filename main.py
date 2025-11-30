import logging
import os

from services.config_log import set_up_logging
from services.crawler import One_zero_four_crawler
from services.db import MongoDB_one_zero_four
from services.cleaner import Cleaner

set_up_logging(debug=True)
logger = logging.getLogger(__name__)

class Main:
    def __init__(self):
        # 有在猶豫是否要弄成 class, 最終決定避免在一次任務中需要重複建立其他功能 class 
        self.crawler = One_zero_four_crawler()
        self.db = MongoDB_one_zero_four()
        self.cleaner = Cleaner()

    def fetch_data_and_save_to_db(self, keyword:str, area:str):
        if not isinstance(keyword, str) and not isinstance(area, str):
            logger.error("Keyword and area must be strings.")
            return

        try:
            # 爬取資料
            self.crawler = One_zero_four_crawler()
            datas = self.crawler.job_cleaned_pipeline_bronze(keyword, area)
        except Exception as e:
            logger.exception(f"Failed to crawl data: {e}")

        # 將資料存入資料庫
        try:
            self.db.insert_into_bronze(datas)
        except Exception as e:
            logger.exception(f"Failed to connection to MongoDB:{e}")


    def output_jobname_and_skill_and_specialty_as_3_csv(self, job_name_include_regex, file_title):
        # 從資料庫取出資料, pattern: Data from bronze
        condition = {"header.jobName": {"$regex": job_name_include_regex, "$options": "i"}}
        projection = {"header": 1, "condition": 1, "_id": 1}
        documents = self.db.select_from_bronze(condition, projection)

        # 將資料轉換成 DF
        original_df = self.cleaner._use_header_condition_id_make_df(documents)

        # get job_name with job_id 作為映射主表
        job_name = self.cleaner._make_jobid_with_jobname(original_df)

        # skill
        skill = self.cleaner._make_job_skill_or_specialty(original_df, "skill")

        # speciately
        specialty = self.cleaner._make_job_skill_or_specialty(original_df, "specialty")

        input_dfs = {"job_name": job_name, "skills": skill, "specialtys": specialty}

        # 將資料輸出成 csv 格式, 以便 PowerBI 使用
        if not os.path.exists("results"):
            os.mkdir("results")

        for name, df in input_dfs.items():
            df.to_csv(f"results/{file_title}_{name}.csv", index=False)

    # def main():
    # 用 argument 讓 user 控制程序的行為 [fetch and save | select and draw | fetch and save, and then select and draw]

if __name__ == "__main__":
    main = Main()
    # next kw: 後端工程
    keyword = "資料工程"
    area = "台北市"
    main.fetch_data_and_save_to_db(keyword, area)

    # job_name_include_regex = "Python"
    # file_title = "taipei_python"
    # main.output_jobname_and_skill_and_specialty_as_3_csv(job_name_include_regex, file_title)