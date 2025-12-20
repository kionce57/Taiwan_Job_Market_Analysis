import logging
from typing import Literal, cast

import numpy as np
import pandas as pd
from pandera.typing import DataFrame

from src.interfaces.dtos import (
    Category,
    CustInfo,
    DimJob,
    JobDetail,
    Language,
    Major,
    Skills,
    Specialties,
    Welfare,
)

logger = logging.getLogger(__name__)


def _classify_job_title(title: str) -> str:
    """
    將職缺名稱映射至標準化工程職位類別。
    採用優先級匹配策略 (Priority Matching Strategy)。

    Args:
        title (str): 原始職缺名稱

    Returns:
        str: 標準化類別名稱
    """
    if not isinstance(title, str):
        return "Unknown"

    t = title.lower()

    # 1. AI / ML (優先級最高，避免被歸類為 Python Engineer)
    if any(
        kw in t
        for kw in [
            "ai",
            "artificial intelligence",
            "machine learning",
            "deep learning",
            "computer vision",
            "nlp",
            "algorithm",
            "人工智慧",
            "機器學習",
            "演算法",
            "深度學習",
            "影像識別",
            "自然語言",
            "llm",
            "gpt",
        ]
    ):
        return "AI Engineer / Researcher"

    # 2. Data Roles (科學家與分析師)
    if any(
        kw in t
        for kw in ["data scientist", "data analyst", "mining", "資料科學", "數據分析", "資料分析"]
    ):
        return "Data Scientist / Analyst"

    # 3. Data Engineering (數據工程)
    if any(
        kw in t
        for kw in [
            "data engineer",
            "etl",
            "big data",
            "spark",
            "hadoop",
            "pipeline",
            "資料工程",
            "數據工程",
        ]
    ):
        return "Data Engineer"

    # 4. Infrastructure & Cloud
    if any(
        kw in t
        for kw in [
            "devops",
            "sre",
            "site reliability",
            "cloud",
            "aws",
            "gcp",
            "azure",
            "kubernetes",
            "docker",
            "cicd",
            "雲端",
            "系統工程",
            "運維",
        ]
    ):
        return "DevOps / SRE / Cloud Engineer"

    # 5. QA & Automation
    if any(kw in t for kw in ["qa", "test", "automation", "sdet", "測試", "自動化", "品保"]):
        return "QA / Automation Engineer"

    # 6. Embedded / Firmware (硬體相關)
    if any(kw in t for kw in ["firmware", "embedded", "driver", "fpga", "韌體", "嵌入式", "驅動"]):
        return "Embedded / Firmware Engineer"

    # 7. Web Development (全端優先於前後端)
    if any(kw in t for kw in ["fullstack", "full-stack", "全端"]):
        return "Fullstack Engineer"

    if any(
        kw in t
        for kw in [
            "frontend",
            "front-end",
            "react",
            "vue",
            "angular",
            "javascript",
            "html",
            "ui",
            "ux",
            "web",
            "前端",
        ]
    ):
        return "Frontend Engineer"

    # 後端 (包含常見後端語言，若前述未匹配則落入此區)
    if any(
        kw in t
        for kw in [
            "backend",
            "back-end",
            "server",
            "php",
            "java",
            "golang",
            "ruby",
            "node",
            "c#",
            ".net",
            "django",
            "flask",
            "spring",
            "後端",
        ]
    ):
        return "Backend Engineer"

    # 8. General / Fallback (通用軟體工程師)
    if any(
        kw in t
        for kw in [
            "software engineer",
            "developer",
            "programmer",
            "python",
            "c++",
            "engineer",
            "工程師",
            "軟體",
        ]
    ):
        return "General Software Engineer"

    return "Others"


def make_original_df(documents: list[dict | list]) -> pd.DataFrame:
    try:
        df = pd.DataFrame(documents)
        return df
    except (KeyError, ValueError, TypeError) as e:
        logger.exception(f"Failed to convert documents to DataFrame: {e}")
        raise


# 製作 job_id with skill 的 df
def make_job_skill_or_specialty(
    original_df: pd.DataFrame, mode: Literal["skill", "specialty"]
) -> pd.DataFrame:
    purpose = str(mode)

    if purpose not in ["skill", "specialty"]:
        raise ValueError("purpose must be 'skill' or 'specialty'")

    try:
        cp_ori_df = original_df[["_id", "condition"]].copy()
        cp_ori_df[purpose] = cp_ori_df["condition"].apply(lambda x: x.get(purpose))

        # 因為 reset index 所以每個 dict 會佔據一 row, 因此對其解 json 後形成的 df 跟 exploded 的 index 相符
        exploded_df = cp_ori_df.explode(purpose).reset_index()
        exploded_df = exploded_df.dropna(subset=[purpose])

        id_with_purpose_df = exploded_df[["_id", purpose]].reset_index(drop=True)

        description_df = pd.json_normalize(id_with_purpose_df[purpose].to_list())

        df_final = pd.concat([id_with_purpose_df, description_df], axis=1)
        df_final = df_final.drop(columns=[purpose, "code"])

        return df_final
    except (KeyError, ValueError, TypeError) as e:
        logger.exception(f"Failed to make {purpose} DataFrame: {e}")
        raise


def make_cust_df(original_df: pd.DataFrame) -> pd.DataFrame:
    cust_df = original_df[["custNo", "industry", "employees"]].copy()

    # 從 nested 結構中拿 custname, 先取出 -> 變 list[dict] -> json_normalize 抽出所有的 key 變成 df
    header = original_df["header"]
    header_list = header.to_list()
    header_df = pd.json_normalize(header_list)

    cust_df.loc[:, "cust_name"] = header_df["custName"].values

    cust_df.loc[:, "employees"] = (
        cust_df["employees"]
        .astype(str)
        .str.replace(r"[^\d]", "", regex=True)  # 只保留數字，去掉"人"或其他文字
        .replace("", "0")  # 處理原本就是空字串或"暫不提供"的情況
    )
    cust_df.loc[:, "employees"] = cust_df["employees"].fillna("0").astype(int)
    cust_df.rename(columns={"custNo": "cust_no"}, inplace=True)

    validate_df = CustInfo.validate(cust_df)

    return cast(DataFrame[CustInfo], validate_df)


def make_dim_job(original_df: pd.DataFrame) -> pd.DataFrame:
    dim_job = original_df[["job_id", "custNo"]].copy()

    header_sub = pd.json_normalize(original_df["header"].to_list()).loc[
        :, ["jobName", "appearDate"]
    ]

    condi_sub = pd.json_normalize(original_df["condition"].to_list()).loc[:, ["edu", "workExp"]]

    job_detail_sub = pd.json_normalize(original_df["jobDetail"].to_list())[
        [
            "salaryMin",
            "salaryMax",
            "salaryType",
            "workType",
            "addressArea",
            "addressRegion",
            "workPeriod",
            "vacationPolicy",
        ]
    ]

    dim_job = pd.concat([dim_job, header_sub], axis=1)

    dim_job = pd.concat([dim_job, condi_sub], axis=1)

    dim_job = pd.concat([dim_job, job_detail_sub], axis=1)
    dim_job["salary_min"] = dim_job["salaryMin"].astype(int)
    dim_job["salary_max"] = dim_job["salaryMax"].astype(int)
    dim_job["salary_type"] = dim_job["salaryType"].astype(int)

    dim_job.drop(columns=["salaryMin", "salaryMax", "salaryType"], inplace=True)

    # 改名
    column_mapping: dict[str, str] = {
        "jobName": "job_name",
        "appearDate": "appear_date",
        "custNo": "cust_no",
        "workExp": "work_exp",
        "workType": "work_type",
        "addressArea": "address_area",
        "addressRegion": "address_region",
        "workPeriod": "work_period",
        "vacationPolicy": "vacation_policy",
    }

    # 2. 執行改名
    # inplace=True 代表直接修改 dim_job 本體
    dim_job.rename(columns=column_mapping, inplace=True)

    # 將 [] 補成 Nan
    mask = dim_job["work_type"].apply(lambda x: x == [])
    dim_job.loc[mask, "work_type"] = np.nan

    # 轉成日期 type
    dim_job["appear_date"] = pd.to_datetime(
        dim_job["appear_date"], format="%Y/%m/%d", errors="coerce"
    )

    validate_df = DimJob.validate(dim_job)
    return cast(DataFrame[DimJob], validate_df)


# 要先拿到 dim job table 的 id with job_id, 後續的 dataframe 才能根據 job_id merge, 獲得 job 在 SQL 的 id


def _merge_job_uid(original_df: pd.DataFrame, job_uid_df: pd.DataFrame) -> pd.DataFrame:
    """
    將原始 DataFrame 與 job_uid_df 進行 merge，獲取資料庫內的 job_uid。

    Args:
        original_df: 原始資料 DataFrame，必須包含 job_id 欄位
        job_uid_df: 包含 job_id 與 id (資料庫主鍵) 映射的 DataFrame

    Returns:
        合併後的 DataFrame，包含 job_uid 欄位
    """
    # 資料庫中 dim_job 的主鍵叫 id，這裡重新命名為 job_uid 供內部使用
    uid_df = job_uid_df[["job_id", "id"]].rename(columns={"id": "job_uid"})
    merged = original_df.merge(uid_df, on="job_id", how="left")
    return merged


def make_job_detail(original_df: pd.DataFrame, job_uid_df: pd.DataFrame) -> pd.DataFrame:
    """
    製作 JobDetail DataFrame。

    Args:
        original_df: 原始資料 DataFrame
        job_uid_df: 包含 job_id 與 job_uid 映射的 DataFrame

    Returns:
        符合 JobDetail Schema 的 DataFrame
    """
    try:
        merged_df = _merge_job_uid(original_df, job_uid_df)

        job_detail_sub = pd.json_normalize(merged_df["jobDetail"].to_list())[
            ["needEmp", "manageResp", "businessTrip", "remoteWork", "jobDescription"]
        ]

        result_df = pd.DataFrame(
            {
                "job_uid": merged_df["job_uid"],
                "need_emp": job_detail_sub["needEmp"],
                "manage_resp": job_detail_sub["manageResp"],
                "business_trip": job_detail_sub["businessTrip"],
                "remote_work": job_detail_sub["remoteWork"],
                "job_description": job_detail_sub["jobDescription"],
            }
        )

        validate_df = JobDetail.validate(result_df)
        return cast(DataFrame[JobDetail], validate_df)

    except (KeyError, ValueError, TypeError) as e:
        logger.exception(f"Failed to make JobDetail DataFrame: {e}")
        raise


def make_welfare(original_df: pd.DataFrame, job_uid_df: pd.DataFrame) -> pd.DataFrame:
    """
    製作 Welfare DataFrame。

    Args:
        original_df: 原始資料 DataFrame
        job_uid_df: 包含 job_id 與 job_uid 映射的 DataFrame

    Returns:
        符合 Welfare Schema 的 DataFrame
    """
    try:
        merged_df = _merge_job_uid(original_df, job_uid_df)

        welfare_sub = pd.json_normalize(merged_df["welfare"].to_list())[
            ["tag", "welfare", "legalTag"]
        ]

        result_df = pd.DataFrame(
            {
                "job_uid": merged_df["job_uid"],
                "tags": welfare_sub["tag"],
                "welfare_description": welfare_sub["welfare"],
                "legal_tags": welfare_sub["legalTag"],
            }
        )

        validate_df = Welfare.validate(result_df)
        return cast(DataFrame[Welfare], validate_df)

    except (KeyError, ValueError, TypeError) as e:
        logger.exception(f"Failed to make Welfare DataFrame: {e}")
        raise


def make_major(original_df: pd.DataFrame, job_uid_df: pd.DataFrame) -> pd.DataFrame:
    """
    製作 Major DataFrame (一對多關係表)。

    Args:
        original_df: 原始資料 DataFrame
        job_uid_df: 包含 job_id 與 job_uid 映射的 DataFrame

    Returns:
        符合 Major Schema 的 DataFrame
    """
    try:
        merged_df = _merge_job_uid(original_df, job_uid_df)

        # 取出 major 欄位 (是一個 list of strings)
        cp_df = merged_df[["job_uid", "condition"]].copy()
        cp_df["major"] = cp_df["condition"].apply(lambda x: x.get("major", []))

        # 展開一對多關係
        exploded_df = cp_df.explode("major").reset_index(drop=True)
        exploded_df = exploded_df.dropna(subset=["major"])
        exploded_df = exploded_df[exploded_df["major"] != ""]

        result_df = exploded_df[["job_uid", "major"]].rename(columns={"major": "major_name"})

        if result_df.empty:
            # 如果沒有資料，返回空的符合 schema 的 DataFrame
            return pd.DataFrame(columns=["job_uid", "major_name"])

        validate_df = Major.validate(result_df)
        return cast(DataFrame[Major], validate_df)

    except (KeyError, ValueError, TypeError) as e:
        logger.exception(f"Failed to make Major DataFrame: {e}")
        raise


def make_skills(original_df: pd.DataFrame, job_uid_df: pd.DataFrame) -> pd.DataFrame:
    """
    製作 Skills DataFrame (一對多關係表)。

    Args:
        original_df: 原始資料 DataFrame
        job_uid_df: 包含 job_id 與 job_uid 映射的 DataFrame

    Returns:
        符合 Skills Schema 的 DataFrame
    """
    try:
        merged_df = _merge_job_uid(original_df, job_uid_df)

        cp_df = merged_df[["job_uid", "condition"]].copy()
        cp_df["skill"] = cp_df["condition"].apply(lambda x: x.get("skill", []))

        exploded_df = cp_df.explode("skill").reset_index(drop=True)
        exploded_df = exploded_df.dropna(subset=["skill"])

        # 解析 dict 結構取得 description
        skill_desc = pd.json_normalize(exploded_df["skill"].to_list())

        result_df = pd.DataFrame(
            {"job_uid": exploded_df["job_uid"].values, "skill_name": skill_desc["description"]}
        )

        if result_df.empty:
            return pd.DataFrame(columns=["job_uid", "skill_name"])

        validate_df = Skills.validate(result_df)
        return cast(DataFrame[Skills], validate_df)

    except (KeyError, ValueError, TypeError) as e:
        logger.exception(f"Failed to make Skills DataFrame: {e}")
        raise


def make_specialties(original_df: pd.DataFrame, job_uid_df: pd.DataFrame) -> pd.DataFrame:
    """
    製作 Specialties DataFrame (一對多關係表)。

    Args:
        original_df: 原始資料 DataFrame
        job_uid_df: 包含 job_id 與 job_uid 映射的 DataFrame

    Returns:
        符合 Specialties Schema 的 DataFrame
    """
    try:
        merged_df = _merge_job_uid(original_df, job_uid_df)

        cp_df = merged_df[["job_uid", "condition"]].copy()
        cp_df["specialty"] = cp_df["condition"].apply(lambda x: x.get("specialty", []))

        exploded_df = cp_df.explode("specialty").reset_index(drop=True)
        exploded_df = exploded_df.dropna(subset=["specialty"])

        specialty_desc = pd.json_normalize(exploded_df["specialty"].to_list())

        result_df = pd.DataFrame(
            {
                "job_uid": exploded_df["job_uid"].values,
                "specialty_name": specialty_desc["description"],
            }
        )

        if result_df.empty:
            return pd.DataFrame(columns=["job_uid", "specialty_name"])

        validate_df = Specialties.validate(result_df)
        return cast(DataFrame[Specialties], validate_df)

    except (KeyError, ValueError, TypeError) as e:
        logger.exception(f"Failed to make Specialties DataFrame: {e}")
        raise


def make_category(original_df: pd.DataFrame, job_uid_df: pd.DataFrame) -> pd.DataFrame:
    """
    製作 Category DataFrame (一對多關係表)。

    Args:
        original_df: 原始資料 DataFrame
        job_uid_df: 包含 job_id 與 job_uid 映射的 DataFrame

    Returns:
        符合 Category Schema 的 DataFrame
    """
    try:
        merged_df = _merge_job_uid(original_df, job_uid_df)

        # jobCategory 在 jobDetail 內
        job_detail_list = merged_df["jobDetail"].to_list()
        cp_df = pd.DataFrame(
            {
                "job_uid": merged_df["job_uid"],
                "jobCategory": [jd.get("jobCategory", []) for jd in job_detail_list],
            }
        )

        exploded_df = cp_df.explode("jobCategory").reset_index(drop=True)
        exploded_df = exploded_df.dropna(subset=["jobCategory"])

        category_desc = pd.json_normalize(exploded_df["jobCategory"].to_list())

        result_df = pd.DataFrame(
            {
                "job_uid": exploded_df["job_uid"].values,
                "category_name": category_desc["description"],
            }
        )

        if result_df.empty:
            return pd.DataFrame(columns=["job_uid", "category_name"])

        validate_df = Category.validate(result_df)
        return cast(DataFrame[Category], validate_df)

    except (KeyError, ValueError, TypeError) as e:
        logger.exception(f"Failed to make Category DataFrame: {e}")
        raise


def make_language(original_df: pd.DataFrame, job_uid_df: pd.DataFrame) -> pd.DataFrame:
    """
    製作 Language DataFrame (一對多關係表)。

    Args:
        original_df: 原始資料 DataFrame
        job_uid_df: 包含 job_id 與 job_uid 映射的 DataFrame

    Returns:
        符合 Language Schema 的 DataFrame
    """
    try:
        merged_df = _merge_job_uid(original_df, job_uid_df)

        cp_df = merged_df[["job_uid", "condition"]].copy()
        cp_df["language"] = cp_df["condition"].apply(lambda x: x.get("language", []))

        exploded_df = cp_df.explode("language").reset_index(drop=True)
        exploded_df = exploded_df.dropna(subset=["language"])

        if exploded_df.empty:
            return pd.DataFrame(
                columns=["job_uid", "language", "listening", "speaking", "reading", "writing"]
            )

        # 解析 language dict 結構
        lang_list = exploded_df["language"].to_list()
        lang_records = []
        for idx, lang_item in enumerate(lang_list):
            ability = lang_item.get("ability", {})
            lang_records.append(
                {
                    "job_uid": exploded_df.iloc[idx]["job_uid"],
                    "language": lang_item.get("language", ""),
                    "listening": ability.get("listening", ""),
                    "speaking": ability.get("speaking", ""),
                    "reading": ability.get("reading", ""),
                    "writing": ability.get("writing", ""),
                }
            )

        result_df = pd.DataFrame(lang_records)

        if result_df.empty:
            return pd.DataFrame(
                columns=["job_uid", "language", "listening", "speaking", "reading", "writing"]
            )

        validate_df = Language.validate(result_df)
        return cast(DataFrame[Language], validate_df)

    except (KeyError, ValueError, TypeError) as e:
        logger.exception(f"Failed to make Language DataFrame: {e}")
        raise
