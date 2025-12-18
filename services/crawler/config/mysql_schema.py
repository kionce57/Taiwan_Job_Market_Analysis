from sqlalchemy import (
    Table, 
    Column, 
    Integer, 
    String, 
    BigInteger, 
    Date, 
    MetaData, 
    ForeignKey, 
    Index, 
    text,
    func
)
# 用 Core 模式, 不需要 ORM
# 固定結構的 database 用全域宣告就好

# 初始化元數據容器
metadata_obj: MetaData = MetaData()

# 1. 公司維度表 (cust_info)
# 用途：儲存公司基本資料，dim_job 的弱關聯參照對象
cust_info: Table = Table(
    "cust_info",
    metadata_obj,
    Column("cust_no", String(24), primary_key=True, comment="統編/代號"),
    Column("cust_name", String(250)),
    Column("industry", String(100)),
    Column("employees", Integer, comment="清洗後的數字")
)

# 2. 薪水類別 (salary_type)
# 用途：薪資區間的列舉定義
salary_type: Table = Table(
    "salary_type",
    metadata_obj,
    Column("type", Integer, primary_key=True),
    Column("name", String(16))
)

# 3. 職缺主表 (dim_job)
# 用途：核心事實表，包含職缺詳細資訊、薪資與地理位置索引
dim_job: Table = Table(
    "dim_job",
    metadata_obj,
    # --- 主鍵與業務鍵 ---
    Column("id", BigInteger, primary_key=True, autoincrement=True, comment="內部代理鍵"),
    Column("job_id", String(40), nullable=False, unique=True, comment="外部業務鍵"),
    Column("job_name", String(250)),
    Column("work_type", String(30)),

    # --- 薪資與獎金 (FK & Defaults) ---
    # 注意: SQL 中 DEFAULT '30' 對應 text("'30'")，雖欄位是 INT 但 DB 通常允許隱式轉換
    Column("salary_type", Integer, ForeignKey("salary_type.type"), server_default=text("'30'")),
    Column("salary_min", Integer, server_default=text("0")),
    Column("salary_max", Integer, server_default=text("0")),

    # --- 核心維度 ---
    Column("address_area", String(20)),
    Column("district", String(30)),
    Column("address_region", String(100)),
    Column("edu", String(100)),
    Column("work_period", String(50)),
    Column("vacation_policy", String(50)),

    # --- 元數據與弱關聯 ---
    # 這裡不設 ForeignKey，僅保留欄位以符合 "弱關聯" 需求
    Column("cust_no", String(24)), 
    Column("appear_date", Date),
    # 使用 func.now() 對應 SQL 的 now()
    Column("updated_date", Date, server_default=func.now()),

    # --- 索引定義 (依據 SQL 需求) ---
    # Index(索引名稱, 欄位1, 欄位2...)
    Index("idx_salary", "salary_min"),
    Index("idx_location", "city", "district"), # 複合索引
    Index("idx_job_id", "job_id"),             # 雖然 unique=True 已隱含索引，但依需求顯式宣告
    Index("idx_cust", "cust_no")
)