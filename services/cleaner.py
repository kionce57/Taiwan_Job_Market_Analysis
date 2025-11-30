import logging

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
def make_job_skill_or_specialty(original_df: pd.DataFrame, skill_or_specialty: str) -> pd.DataFrame:
    purpose = str(skill_or_specialty)

    if purpose not in ["skill", "specialty"]:
        raise ValueError("purpose must be 'skill' or 'specialty'")

    try:
        cp_ori_df = original_df[["_id", "condition"]].copy()
        cp_ori_df[purpose] = cp_ori_df["condition"].apply(lambda x: x.get(purpose))

        # 因為 reset index 所以每個 dict 會佔據一 row, 因此對其解 json 後形成的 df 跟 exploded 的 index 相符
        exploded_df = cp_ori_df.explode(purpose).reset_index()
        exploded_df = exploded_df.dropna(subset=[purpose])

        id_with_purpose_df = exploded_df[["_id", purpose]]

        description_df = pd.json_normalize(id_with_purpose_df[purpose])

        df_final = pd.concat([id_with_purpose_df, description_df], axis=1)
        df_final = df_final.drop(columns=[purpose, "code"])

        return df_final
    except (KeyError, ValueError, TypeError) as e:
        logger.exception(f"Failed to make {purpose} DataFrame: {e}")


def _make_id_with_salary_df(original_df: pd.DataFrame) -> pd.DataFrame:
    try:
        cp_ori_df = original_df.copy()
        json_normalized_df = pd.json_normalize(cp_ori_df["jobDetail"])[["salary", "salaryMin", "salaryMax"]]
        # axis=1, is mean 以 row 為標準合併, index=0 與 index=0 join 以此類推
        salary_df = pd.concat([cp_ori_df, json_normalized_df], axis=1)

        salary_df = salary_df.drop(columns="jobDetail", axis=1)

        return salary_df
    except (KeyError, ValueError, TypeError) as e:
        logger.exception(f"Failed to make salary DataFrame: {e}")


def exact_salary(original_df: pd.DataFrame) -> pd.DataFrame:
    """
    salaryType=50 is 月薪(會包含 xxx 以上)
    """
    cp_ori_df = original_df.copy()

    json_normalized_df = pd.json_normalize(cp_ori_df["jobDetail"].to_list())[["salary", "salaryMin", "salaryMax", "salaryType"]]
    
    # axis=1, 表示以 row 為標準合併, index=0 與 index=0 join 以此類推
    salary_df = pd.concat([cp_ori_df, json_normalized_df], axis=1)
    salary_df = salary_df.drop(columns="jobDetail", axis=1)

    mask = (salary_df["salaryType"] == 50) & (salary_df["salaryMin"] > 0) & (salary_df["salaryMax"] < 5000000)
    month_salary = salary_df[mask]
    month_salary = month_salary[["_id", "salaryMin", "salaryMax"]]
    
    return month_salary

def negotiable_salary():
    """
    B 群：面議與無上限的職缺 (Negotiable/Open-Ended)
        目標：分析「技能關鍵字」與「資深程度」。
        處理：不分析金額（因為是未知的）。
        分析 Text Mining：這群職缺的 jobDescription 裡，哪些關鍵字出現頻率最高？（例如：System Design, Architecture, Lead, Cloud Native）。
        洞察：這告訴你「想要拿到 40k+ 甚至年薪百萬，我需要具備哪些非量化的特質」。
    """
