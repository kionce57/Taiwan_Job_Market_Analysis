import json
import logging
import random
import re
import time
import urllib.parse
from collections.abc import Iterator
from pathlib import Path

import requests

from src.interfaces.interfaces import Crawler

# 訪問 104, headers 需要有 User-Agent and 正確的 Referer value
# request 時要注意 pagesize <= 30 will fetched {'error': {'code': 422, 'message': 'pagesize must be less than or equal to 30', 'details': []}}
# 當呼叫的 page 超過內容物時, 會 return "data" 內為 empty list 的 dict
# 其實可以不用給 pagesize, 但會不好控制 page 上限, 故 30

logger = logging.getLogger(__name__)


class OneZeroFourCrawler(Crawler):
    NOISE_COLUMNS = [
        "corpImageRight",
        "environmentPic",
        "switch",
        "custLogo",
        "postalCode",
        "closeDate",
        "reportUrl",
        "industryNo",
        "chinaCorp",
        "interactionRecord",
    ]
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    }
    DETAIL_URL_PATTERN = "https://www.104.com.tw/job/ajax/content/"
    BASE_URL = "https://www.104.com.tw/jobs/search/api/jobs"

    def __init__(self):
        file = Path(__file__).parent.parent / "utils" / "area_category_for_transformer.json"
        # 建議加入錯誤處理，若檔案不存在
        if file.exists():
            with open(file, encoding="utf-8") as f:
                self._area_num_mapping = json.load(f)
        else:
            self._area_num_mapping = {}

    def harvest_jobs(self, keyword: str, area: str, max_pages: int = 30) -> Iterator[dict]:
        """
        [ETL: Extract]
        主入口：負責「收割」工作資料。
        使用 Generator (yield) 模式，爬一筆回傳一筆，更適合串流處理與容錯。
        """
        logger.info(f"Start harvesting jobs for keyword: {keyword}")

        # 1. 搜尋階段 (Discovery)
        try:
            for page in range(1, max_pages + 1):
                logger.debug(f"Scanning page {page}...")
                job_listings = self._discover_job_listings(keyword, area, page)

                if not job_listings:
                    logger.info("No more jobs found.")
                    break

                # 2. 抓取詳情階段 (Retrieval & Sanitization)
                for listing in job_listings:
                    job_data = self._fetch_and_sanitize_detail(listing)
                    if job_data:
                        yield job_data  # 立即回傳，讓呼叫端決定何時存入 Bronze
                        time.sleep(random.uniform(1.5, 4))

                time.sleep(random.uniform(1, 3))
        except Exception as e:
            logger.exception(f"The error occurred when harvser jobs: {e}")
            return

    def _create_headers(self, area_num, url_parsed_keyword, page):
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Host": "www.104.com.tw",
            "Referer": f"https://www.104.com.tw/jobs/search/?area={area_num}&jobsource=joblist_search&keyword={url_parsed_keyword}&mode=s&page={page}",
            **self.DEFAULT_HEADERS,
        }
        return headers

    def _discover_job_listings(self, keyword: str, area: str, page: int) -> list[dict]:
        """負責與 104 列表 API 互動，回傳含有 job_id 與 link 的基礎資訊"""
        area_num = self._area_num_mapping.get(area, "6001001000")  # Default or error handle
        url_parsed_keyword = urllib.parse.quote(keyword)

        headers = self._create_headers(area_num, url_parsed_keyword, page)
        params = {
            "area": area_num,
            "jobsource": "joblist_search",
            "keyword": keyword,
            "mode": "s",
            "page": page,
            "pagesize": 30,
        }

        try:
            resp = requests.get(self.BASE_URL, headers=headers, params=params)
            resp.raise_for_status()
            jobs: list = resp.json().get("data", [])
            return jobs if isinstance(jobs, list) else []
        except Exception as e:
            logger.exception(f"Failed to discover jobs on page {page}: {e}")
            return []

    def _fetch_and_sanitize_detail(self, listing: dict) -> dict | None:
        """
        負責抓取單一工作詳情並進行「輕度清洗 (Sanitize)」。
        """
        # 1. 解析 ID (Parser)
        link = listing.get("link", {}).get("job", "")
        match = re.search(r"/job/(\w+)", link)
        if not match:
            return None

        job_id = match.group(1)
        api_url = f"{self.DETAIL_URL_PATTERN}{job_id}"

        # 2. 網路請求 (Fetcher)
        try:
            resp = requests.get(api_url, headers={"Referer": api_url, **self.DEFAULT_HEADERS})
            resp.raise_for_status()
            raw_json = resp.json()
        except Exception as e:
            logger.exception(f"Failed to fetch detail for {job_id}: {e}")
            return None

        # 3. 輕度清洗 (Sanitizer) - 這裡就是你的特定網頁邏輯
        payload = raw_json.get("data", {})

        # 移除 Header 雜訊
        if "header" in payload and isinstance(payload["header"], dict):
            payload["header"].pop("corpImageTop", None)

        # 移除頂層雜訊
        for col in self.NOISE_COLUMNS:
            payload.pop(col, None)

        # 4. 包裝回傳 (Packaging)
        return {"job_id": job_id, **payload}


if __name__ == "__main__":
    a = OneZeroFourCrawler()
    print(1234)
