import pandas as pd
import pandera as pa
from pandera.typing import Series


class Cust_info(pa.DataFrameSchema):
    cust_no: Series[str] = pa.Field(coerce=True)
    cust_name: Series[str] = pa.Field()
    industry: Series[str] = pa.Field()
    employees: Series[int] = pa.Field()


class DimJob(pa.DataFrameSchema):
    # cust_no 如果是 int type 又是 0 開頭的話, 存入 SQL 開頭的 0 會被抹除, 這樣編號就錯了
    # pa.Field() 預設 nullable=False, 呼應資料處理的正規化理論
    job_id: Series[str] = pa.Field(coerce=True)
    job_title: Series[str] = pa.Field()
    salary_min: Series[int] = pa.Field(coerce=True)
    salary_max: Series[int] = pa.Field(coerce=True)
    work_exp: Series[str] = pa.Field()
    has_bonus: Series[int] = pa.Field(coerce=True)
    avg_bonus_months: Series[float] = pa.Field(nullable=True, coerce=True)
    edu: Series[str] = pa.Field(nullable=True)
    city: Series[str] = pa.Field()
    district: Series[str] = pa.Field()
    work_period: Series[str] = pa.Field()
    vacation_policy: Series[str] = pa.Field(nullable=True)
    cust_no: Series[str] = pa.Field()
    appear_date: Series[pd.Timestamp] = pa.Field(coerce=True)
    updated_date: Series[pd.Timestamp] = pa.Field(coerce=True)


class Major(pa.DataFrameSchema):
    job_uid: Series[int] = pa.Field(coerce=True)
    major: Series[str] = pa.Field


class JobDetail(pa.DataFrameSchema):
    job_uid: Series[int] = pa.Field(coerce=True)
    need_emp: Series[str] = pa.Field()
    manage_resp: Series[str] = pa.Field()
    business_trip: Series[str] = pa.Field()


class Skills(pa.DataFrameSchema):
    job_uid: Series[int] = pa.Field(coerce=True)
    skill_name: Series[str] = pa.Field()


class Specialties(pa.DataFrameSchema):
    job_uid: Series[int] = pa.Field(coerce=True)
    specialty_name: Series[str] = pa.Field()


class Welfare(pa.DataFrameSchema):
    job_uid: Series[int] = pa.Field(coerce=True)
    Welfare_description: Series[str] = pa.Field()


class Category(pa.DataFrameSchema):
    job_uid: Series[int] = pa.Field(coerce=True)
    category_name: Series[str] = pa.Field()


class Language(pa.DataFrameSchema):
    job_uid: Series[int] = pa.Field(coerce=True)
    language: Series[str] = pa.Field()
    listening: Series[str] = pa.Field()
    speaking: Series[str] = pa.Field()
    reading: Series[str] = pa.Field()
    writing: Series[str] = pa.Field()
