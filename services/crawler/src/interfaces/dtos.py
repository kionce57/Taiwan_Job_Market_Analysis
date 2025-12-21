import pandas as pd
import pandera.pandas as pa
from pandera.typing import Series


class CustInfo(pa.DataFrameModel):
    cust_no: Series[str] = pa.Field()
    cust_name: Series[str] = pa.Field()
    industry: Series[str] = pa.Field()
    employees: Series[int] = pa.Field()

    class Config:
        coerce = True  # 強制轉型 (例如字串 "100" 轉為 數字 100)
        strict = True  # 嚴格模式 (DataFrame 不能有 Schema 未定義的欄位)


class DimJob(pa.DataFrameModel):
    # 注意: id (Auto Increment) 通常在 Insert 前的 DataFrame 不存在，故不列入驗證
    job_id: Series[str] = pa.Field()
    job_name: Series[str] = pa.Field()
    work_type: Series[str] = pa.Field(nullable=True)

    salary_type: Series[int] = pa.Field(isin=[10, 20, 30, 40, 50, 60, 70])
    salary_min: Series[int] = pa.Field(ge=0)
    salary_max: Series[int] = pa.Field(ge=0)

    address_area: Series[str] = pa.Field()
    address_region: Series[str] = pa.Field()
    work_exp: Series[str] = pa.Field(nullable=True)
    edu: Series[str] = pa.Field(nullable=True)
    work_period: Series[str] = pa.Field()
    vacation_policy: Series[str] = pa.Field(nullable=True)

    cust_no: Series[str] = pa.Field()
    appear_date: Series[pd.Timestamp] = pa.Field()

    class Config:
        coerce = True
        strict = True


# --- Details & Bridge Tables ---
# 這些表都依賴 job_uid，請確保 ETL 流程中已取得 dim_job.id 回填至此


class JobDetail(pa.DataFrameModel):
    job_uid: Series[int] = pa.Field()
    need_emp: Series[str] = pa.Field()
    manage_resp: Series[str] = pa.Field(nullable=True)
    business_trip: Series[str] = pa.Field(nullable=True)
    remote_work: Series[str] = pa.Field(nullable=True)
    job_description: Series[str] = pa.Field()

    class Config:
        coerce = True
        strict = True


class Welfare(pa.DataFrameModel):
    job_uid: Series[int] = pa.Field(coerce=True)
    tags: Series[object] = pa.Field()  # list of strings
    welfare_description: Series[str] = pa.Field()
    legal_tags: Series[object] = pa.Field()  # list of strings

    class Config:
        coerce = True  # 強制轉型 (例如字串 "100" 轉為 數字 100)
        strict = True  # 嚴格模式 (DataFrame 不能有 Schema 未定義的欄位)


class Major(pa.DataFrameModel):
    job_uid: Series[int] = pa.Field()
    major_name: Series[str] = pa.Field()

    class Config:
        coerce = True  # 強制轉型 (例如字串 "100" 轉為 數字 100)
        strict = True  # 嚴格模式 (DataFrame 不能有 Schema 未定義的欄位)


class Skills(pa.DataFrameModel):
    job_uid: Series[int] = pa.Field()
    skill_name: Series[str] = pa.Field()

    class Config:
        coerce = True  # 強制轉型 (例如字串 "100" 轉為 數字 100)
        strict = True  # 嚴格模式 (DataFrame 不能有 Schema 未定義的欄位)


class Specialties(pa.DataFrameModel):
    job_uid: Series[int] = pa.Field()
    specialty_name: Series[str] = pa.Field()

    class Config:
        coerce = True  # 強制轉型 (例如字串 "100" 轉為 數字 100)
        strict = True  # 嚴格模式 (DataFrame 不能有 Schema 未定義的欄位)


class Category(pa.DataFrameModel):
    job_uid: Series[int] = pa.Field()
    category_name: Series[str] = pa.Field()

    class Config:
        coerce = True  # 強制轉型 (例如字串 "100" 轉為 數字 100)
        strict = True  # 嚴格模式 (DataFrame 不能有 Schema 未定義的欄位)


class Language(pa.DataFrameModel):
    job_uid: Series[int] = pa.Field()
    language: Series[str] = pa.Field()
    listening: Series[str] = pa.Field()
    speaking: Series[str] = pa.Field()
    reading: Series[str] = pa.Field()
    writing: Series[str] = pa.Field()

    class Config:
        coerce = True  # 強制轉型 (例如字串 "100" 轉為 數字 100)
        strict = True  # 嚴格模式 (DataFrame 不能有 Schema 未定義的欄位)
