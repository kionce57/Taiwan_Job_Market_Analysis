import pandera as pa

from pandera.typing import Series

class DimJob(pa.DataFrameSchema):
    job_id:Series[str] = pa.Field(coerce=True)