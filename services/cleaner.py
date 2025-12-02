import logging
from typing import Literal

import pandas as pd

logger = logging.getLogger(__name__)


def use_original_documents_make_df(documents: list[dict | list]) -> pd.DataFrame:
    try:
        df = pd.DataFrame(documents)
        return df
    except (KeyError, ValueError, TypeError) as e:
        logger.exception(f"Failed to convert documents to DataFrame: {e}")


# 製作 jobnane with job_id 的 df
def make_jobid_with_jobname(original_df: pd.DataFrame) -> pd.DataFrame:
    try:
        cp_ori_df = original_df.copy()

        header_df = pd.json_normalize(cp_ori_df["header"])
        cp_ori_df["job_name"] = header_df["jobName"]

        job_id_name_df = cp_ori_df[["_id", "job_name"]]

        return job_id_name_df

    except (KeyError, ValueError, TypeError) as e:
        logger.exception(f"Failed to make job_id with job_name DataFrame: {e}")


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

        description_df = pd.json_normalize(id_with_purpose_df[purpose])

        df_final = pd.concat([id_with_purpose_df, description_df], axis=1)
        df_final = df_final.drop(columns=[purpose, "code"])

        return df_final
    except (KeyError, ValueError, TypeError) as e:
        logger.exception(f"Failed to make {purpose} DataFrame: {e}")


def _make_id_with_salary_df(original_df: pd.DataFrame) -> pd.DataFrame:
    try:
        cp_ori_df = original_df.copy()
        json_normalized_df = pd.json_normalize(cp_ori_df["jobDetail"])[
            ["salary", "salaryMin", "salaryMax"]
        ]
        # axis=1, is mean 以 row 為標準合併, index=0 與 index=0 join 以此類推
        salary_df = pd.concat([cp_ori_df, json_normalized_df], axis=1)

        salary_df = salary_df.drop(columns="jobDetail", axis=1)

        return salary_df
    except (KeyError, ValueError, TypeError) as e:
        logger.exception(f"Failed to make salary DataFrame: {e}")


def _convert_annual_to_monthly(df, annual_factor=13):
    """
    將年薪 (Type 60) 轉換為月薪，但保護 max == 9999999 的特殊標記。
    """
    # 1. 定義基礎遮罩：找出所有年薪制的資料
    mask_annual = df["salaryType"] == 60

    # 2. 處理 salaryMin (下限)
    # 邏輯：只要是年薪制，下限通常都是有效數字，直接轉換, 0/13 = 0
    df.loc[mask_annual, "salaryMin"] = df.loc[mask_annual, "salaryMin"] // annual_factor

    # 3. 處理 salaryMax (上限) - 加入你要求的功能
    # 邏輯：是年薪制 (Type 60) 且 (AND) 上限不是特殊標記 (Max != 9999999)
    mask_convert_max = mask_annual & (df["salaryMax"] != 9999999)

    # 只有符合上述複合條件的，才進行除法運算
    df.loc[mask_convert_max, "salaryMax"] = df.loc[mask_convert_max, "salaryMax"] // annual_factor

    return df


def process_salary_info(
    original_df: pd.DataFrame, mode: Literal["exact", "negotiable"] = "exact"
) -> pd.DataFrame:
    """
    salaryType=10 is 面議
    salaryType=50 is 月薪(會包含 xxx 以上)
    salaryType=60 is 年薪(會包含 xxx 以上)
    該 func 只處理明確標示薪資上下限的職缺
    """
    if mode not in ["exact", "negotiable"]:
        raise ValueError("exact_or_negotiable must be 'exact' or 'negotiable'")

    cp_ori_df = original_df.copy()

    try:
        json_normalized_df = pd.json_normalize(cp_ori_df["jobDetail"].to_list())[
            ["salary", "salaryMin", "salaryMax", "salaryType"]
        ]

        # axis=1, 表示以 row 為標準合併, index=0 與 index=0 join 以此類推
        salary_df = pd.concat([cp_ori_df, json_normalized_df], axis=1)
        salary_df = salary_df.drop(columns="jobDetail", axis=1)

        if mode == "exact":
            mask_monthly = salary_df["salaryType"] == 50
            mask_annual = salary_df["salaryType"] == 60
            salary_range = (salary_df["salaryMin"] > 0) & (salary_df["salaryMax"] != 9999999)

            monthly_salary = salary_df[(mask_monthly | mask_annual) & salary_range].copy()

        elif mode == "negotiable":
            mask_negotiable = salary_df["salaryType"] == 10
            mask_monthly = salary_df["salaryType"] == 50
            mask_annual = salary_df["salaryType"] == 60
            salary_range = (salary_df["salaryMin"] == 0) & (salary_df["salaryMax"] == 0) | (
                salary_df["salaryMax"] == 9999999
            )

            monthly_salary = salary_df[
                (mask_negotiable | mask_monthly | mask_annual) & salary_range
            ].copy()

        monthly_salary = _convert_annual_to_monthly(monthly_salary)
        monthly_salary = monthly_salary[["_id", "salaryMin", "salaryMax"]].reset_index(drop=True)
        return monthly_salary

    except (KeyError, ValueError, TypeError) as e:
        logger.exception(f"Failed to make {mode} salary DataFrame: {e}")
