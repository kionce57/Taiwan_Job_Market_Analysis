import logging
import os
import urllib.parse
from interfaces.interfaces import JobRepository

from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne
from pymongo.errors import (
    BulkWriteError,
    ConfigurationError,
    OperationFailure,
    ServerSelectionTimeoutError,
)

logger = logging.getLogger(__name__)
load_dotenv()


class MongoDB_one_zero_four(JobRepository):
    DATABASE = "One_zero_four"

    def __init__(self):
        logger.info("Initializing MongoDB connection...")
        mongo_host = os.getenv("MONGO_HOST")
        cluster = os.getenv("CLUSTER")
        db_user = os.getenv("DB_USER")
        db_pwd = os.getenv("DB_PASSWORD")

        # 第一段是 if not all so when all() False 的時候會進入 if 區塊, 因此我們要做的是"找到導致 all() is false" 的 value, 所以是 if not value
        if not all([mongo_host, cluster, db_user, db_pwd]):
            # locals()：這是一個 Python 內建函數，它會回傳一個字典 (Dictionary)，包含當前作用域（Scope）內所有的區域變數, e.g. {variable:value}。
            missing_vars = [
                k
                for k, v in locals().items()
                if not v and k in ["mongo_host", "cluster", "db_user", "db_pwd"]
            ]
            error_msg = f"Missing environment variables: {missing_vars}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        db_user = urllib.parse.quote_plus(db_user)
        db_pwd = urllib.parse.quote_plus(db_pwd)
        uri = f"mongodb+srv://{db_user}:{db_pwd}@{mongo_host}/?appName={cluster}"

        try:
            # Mongo client 採用 lazy 連線, 這裡只是建立 object 並沒有真的 connection to mongo
            self._client: MongoClient = MongoClient(uri)
            self._db = self.client.get_database(MongoDB_one_zero_four.DATABASE)

            # 建立連線, 並檢查是否正確連線
            self._db.command("ping")
            logger.info("Successfully connected to MongoDB Atlas.")

            # MongoDb 的 collection 類似於 MySQL 的 table, 都是 DB 內的頂層
            self._bronze_collection = self.db["bronze"]
        except ConfigurationError as e:
            logger.critical(f"MongoDB Configuration Error (Check dnspython or URI): {e}")
            raise  # 這種錯誤無法自動恢復，往上拋讓程式停止
        except ServerSelectionTimeoutError as e:
            logger.critical(f"Connection Timeout (Check IP Whitelist or Network): {e}")
            raise
        except OperationFailure as e:
            logger.critical(f"Authentication Failed (Check Username/Password): {e}")
            raise

    @property
    def client(self):
        return self._client

    @property
    def db(self):
        return self._db

    @property
    def bronze_collection(self):
        return self._bronze_collection

    def insert_stage(self, datas: list):
        logger.info("Inserting data into MongoDB bronze collection...")
        if not datas:
            logger.warning("The datas list for insert into MongoDB one zero four database is empty")
            return

        operations = []

        for job in datas:
            _id = job["job_id"]

            # 建立 updateone 物件 list, _id 由自己填入, upsert == (_id 存在就)update or (_id 不存在就)insert
            operations.append(UpdateOne({"_id": _id}, {"$set": job}, upsert=True))

        # 平行寫入, when ordered = False, 寫入時某筆發生錯誤, 程式會記錄它, 但不會終止整個 write 程序, 適用於資料順序不重要的時候(e.g. 爬蟲)
        try:
            result = self.bronze_collection.bulk_write(operations, ordered=False)
            # 如果完全沒錯，走這裡
            logger.info(
                f"Batch operation completed. "
                f"Matched (Updated): {result.matched_count}, "
                f"Upserted (New): {result.upserted_count}"
            )

        except BulkWriteError as bwe:
            # 如果部分失敗 (ordered=False)，走這裡
            # bwe.details 裡有成功寫入的統計
            n_inserted = bwe.details.get("nInserted", 0)
            n_matched = bwe.details.get("nMatched", 0)
            n_upserted = bwe.details.get("nUpserted", 0)

            logger.warning(
                f"Batch completed with ERRORS. "
                f"Success: {n_inserted + n_matched + n_upserted}, "
                f"Failed: {len(bwe.details.get('writeErrors', []))}"
            )
            # 紀錄完後，選擇是否要再往上拋出
            raise bwe

    def select_stage(self, job_name_regex: str = None, projection: dict = None) -> list:
        """Bronze stage"""
        """
        要查找集合中的所有文档, 请将空筛选器 {} 传递给find()方法：
        condition pattern: -> like where in MySQL
            {"col":"val"}
            {"col.subcol":"val"} -> 巢狀 query
            { "$and": [{"col":"val"}, {"col":"val"}]}
            { "scores": { "$elemMatch": { "$gt": 80, "$lt": 90 } } } -> 90 >= score >= 80
            { "$or": [ { "version": 4 }, { "name": "Andrea Le" } ] } -> v = 4 or n = Andera
            { "name": { "$not": { "$eq": "Andrea Le" } } } -> name != Andrea
            { "email": { "$regex": "andrea_le" } } -> re.match(r".*andrea_le.*")
        projection pattern: -> like select in MySQL
            {"col": 1} -> 只顯示 col 欄位
            {"col": 0} -> 除了 col 欄位, 都顯示
            {"col.subcol": 1} -> 只顯示 col.subcol 欄位
        """
        logger.debug(
            f"try to select data from bronze collection with regex: {job_name_regex} and projection: {projection}"
        )
        if not job_name_regex:
            condition = {}
        else:
            condition = {"header.jobName": {"$regex": job_name_regex, "$options": "i"}}

        if projection:
            cursor = self.bronze_collection.find(
                condition, max_time_ms=10000, projection=projection
            )
        else:
            cursor = self.bronze_collection.find(condition, max_time_ms=10000)
        # 官方建議使用 for loop, 確保記憶體只有 當下一筆, 不過我的需求簡單, 直接用 list() 把 iterator 變成 list 就好
        result_list = list(cursor)
        logger.debug(f"select data from bronze successfully, total: {len(result_list)}")

        return result_list
