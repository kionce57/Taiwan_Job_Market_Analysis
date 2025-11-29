import logging

from services.config_log import set_up_logging
from services.crawler import One_zero_four_crawler
from services.db import MongoDB_one_zero_four

set_up_logging(debug=True)
logger = logging.getLogger(__name__)

class Main:
    def __init__(self):
        # 有在猶豫是否要弄成 class, 最終決定避免在一次任務中需要重複建立其他功能 class 
        self.crawler = One_zero_four_crawler()
        self.db = MongoDB_one_zero_four()

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
            db = MongoDB_one_zero_four()
            db.insert_into_bronze(datas)
        except Exception as e:
            logger.exception(f"Failed to connection to MongoDB:{e}")


    # def select_data_and_draw(self, condition:dict, projection:dict):
    #     # 從資料庫取出資料
    #     try:
    #         result_by_select = self.db.select_from_bronze(condition, projection)

    #     # 將資料轉換成 DF

    #     # 將資料輸出成 csv 格式, 以便 PowerBI 使用



    # def main():
    # 用 argument 讓 user 控制程序的行為 [fetch and save | select and draw | fetch and save, and then select and draw]

if __name__ == "__main__":
    # fetch_data_and_save_to_db()
    # condition = {"header.jobName": {"$regex": "python", "$options": "i"}}
    # projection = {"header": 1, "condition": 1, "_id": 0}
    # next kw: 後端工程
    main = Main()
    keyword = "資料工程"
    area = "台北市"
    main.fetch_data_and_save_to_db()