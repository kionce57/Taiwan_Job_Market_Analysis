import json
import logging
import random
import re
import time
import urllib.parse
from pathlib import Path

import requests

# 訪問 104, headers 需要有 User-Agent and 正確的 Referer value
# request 時要注意 pagesize <= 30 will fetched {'error': {'code': 422, 'message': 'pagesize must be less than or equal to 30', 'details': []}}
# 當呼叫的 page 超過內容物時, 會 return "data" 內為 empty list 的 dict
# 其實可以不用給 pagesize, 但會不好控制 page 上限, 故 30

logger = logging.getLogger(__name__)


class One_zero_four_crawler:
    PAGESIZE = 30

    def __init__(self):
        file = Path(__file__).parent / "area_category_for_transformer.json"
        with open(file, encoding="utf-8") as f:
            self._area_num_mapping = json.load(f)

    @property
    def area_num_mapping(self):
        return self._area_num_mapping

    def _transformer_area_to_num(self, area: str):
        return self.area_num_mapping[area]

    def _get_job_detail_url_and_jobid(self, keyword, area, page, pagesize=PAGESIZE) -> list[dict]:
        area_num = self._transformer_area_to_num(area)
        url_parsed_keyword = urllib.parse.quote(keyword)

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Host": "www.104.com.tw",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "Referer": f"https://www.104.com.tw/jobs/search/?area={area_num}&jobsource=joblist_search&keyword={url_parsed_keyword}&mode=s&page={page}",
        }

        params = {
            "area": area_num,
            "jobsource": "joblist_search",
            "keyword": keyword,
            "mode": "s",
            "order": "15",
            "page": page,
            "pagesize": pagesize,
        }

        url = "https://www.104.com.tw/jobs/search/api/jobs"
        # requests 會自動對 params 內的參數進行 utf-8 編碼
        # data_format_pattern: after_search_page.json
        try:
            logger.debug(f"Use {keyword} to search job for get job detail url")
            jobs_resp = requests.get(url=url, headers=headers, params=params)
            jobs_resp.raise_for_status()
        except requests.RequestException as e:
            # 處理網路層級的錯誤
            logger.exception(f"Network error when requesting {url}: {e}")

        # 沒工作的話, resp["data"] = []
        jobs = jobs_resp.json().get("data")
        if jobs == []:
            return []

        job_detail_infos = []
        url_pattern = "https://www.104.com.tw/job/ajax/content/"

        logger.debug(f"The number of job: {len(jobs)}")
        for job in jobs:
            try:
                url = job["link"]["job"]
            except KeyError as e:
                logger.exception(f"{job['custName']}-{job['jobName']} not has job link: {e}")
                pass

            regex = r"https://www.104.com.tw/job/(\w*)"
            res = re.match(regex, url)
            job_id = res.group(1)
            url = url_pattern + job_id

            # 在每個資料單位的頂層 col 加入 job_id 是必要的, 它可以讓 db 階段更簡單快速
            job_detail_infos.append({"job_id": job_id, "url": url})

        logger.debug("The job detail urls are prepared")
        return job_detail_infos

    def _get_job_detail(self, url) -> dict | None:
        unneeded_cols = [
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

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "Referer": url,
        }
        try:
            logger.debug(f"Get job detail from {url}")
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()

            try:
                job_detail = resp.json()
            except json.JSONDecodeError as e:
                logger.exception(f"Failed to decode job detail json: {e}")
                return

            job_detail_data = job_detail["data"]
            for col in unneeded_cols:
                job_detail_data.pop(col, None)

            if "header" in job_detail_data:
                job_detail_data["header"].pop("corpImageTop", None)

            return job_detail_data
        except requests.RequestException as e:
            # 處理網路層級的錯誤
            logger.exception(f"Network error when requesting {url}: {e}")

        except KeyError as e:
            logger.exception(f"Failed to get job detail, {e}")

    def job_cleaned_pipeline_bronze(self, keyword, area, pagesize=PAGESIZE) -> list:
        logger.info("Start to fetch job detail")
        job_detail_urls_and_ids = []

        # search job, 以 page 為單位 get 每個工作頁面的 link, 回傳 empty list mean no new job
        for page in range(1, pagesize + 1):
            logger.debug(f"Current page :{page}")
            url_and_id = self._get_job_detail_url_and_jobid(keyword, area, page, pagesize)

            if url_and_id == []:
                break

            job_detail_urls_and_ids.extend(url_and_id)
            time.sleep(random.uniform(1, 3))

        cleaned_job_details = []

        # 遍歷得到的所有 job
        for row in job_detail_urls_and_ids:
            logger.debug(f"fetching {row['job_id']} detail")
            # pattern: cleaned_detail.json
            url = row["url"]
            cleaned_job_detail = self._get_job_detail(url)

            if cleaned_job_detail is None:
                logger.warning(f"The cleaned job detail is None, url:{url}, job_id:{row['job_id']}")
                continue

            cleaned_job_detail["job_id"] = row["job_id"]

            cleaned_job_details.append(cleaned_job_detail)
            time.sleep(random.uniform(1.5, 4))

        # 傳遞給 db class 讓它存到 db 去
        logger.info(
            f"The cleaned job details is prepared, total amount: {len(cleaned_job_details)}"
        )
        return cleaned_job_details
