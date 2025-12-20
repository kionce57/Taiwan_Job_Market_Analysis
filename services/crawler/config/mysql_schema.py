from sqlalchemy import (
    JSON,
    BigInteger,
    Column,
    Date,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    func,
    text,
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
    Column("employees", Integer, comment="清洗後的數字"),
)

# 2. 薪水類別 (salary_type)
# 用途：薪資區間的列舉定義
salary_type: Table = Table(
    "salary_type",
    metadata_obj,
    Column("type", Integer, primary_key=True),
    Column("name", String(16)),
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
    Column("work_type", String(100)),
    # --- 薪資與獎金 ---
    Column("salary_type", Integer, ForeignKey("salary_type.type"), server_default=text("30")),
    Column("salary_min", Integer, server_default=text("0")),
    Column("salary_max", Integer, server_default=text("0")),
    # --- 核心維度 (修正處) ---
    # [修正 1] 對齊 SQL: address_area (20)
    Column("address_area", String(20)),
    # [修正 2] 對齊 SQL: address_region (30), 移除原 district 欄位
    Column("address_region", String(30)),
    # [修正 3] 補回缺失的 work_exp
    Column("work_exp", String(100)),
    Column("edu", String(100)),
    Column("work_period", String(200)),
    Column("vacation_policy", String(200)),
    # --- 元數據與弱關聯 ---
    Column("cust_no", String(24)),
    Column("appear_date", Date),
    Column(
        "updated_date", Date, server_default=text("(CURDATE())")
    ),  # MySQL 需要用 CURDATE() 而非 CURRENT_DATE
    # --- 索引定義 (修正處) ---
    Index("idx_salary", "salary_min"),
    # [修正 4] 索引欄位名稱需與 Column 定義一致 (原為 city, district)
    Index("idx_location", "address_area", "address_region"),
    Index("idx_job_id", "job_id"),
    Index("idx_cust", "cust_no"),
)


# ==========================================
# 3. 職缺細節表 (1:1 Extension)
# ==========================================
job_detail: Table = Table(
    "job_detail",
    metadata_obj,
    # job_uid 同時是 PK 與 FK，構成 1:1 關係
    Column("job_uid", BigInteger, ForeignKey("dim_job.id", ondelete="CASCADE"), primary_key=True),
    Column("need_emp", String(20)),
    Column("manage_resp", String(50)),
    Column("business_trip", String(50)),
    Column("remote_work", String(40)),
    Column("job_description", Text),
    comment="職缺詳細描述擴充表",
)

# ==========================================
# 4. 福利擴充表 (1:1 Extension with JSON)
# ==========================================
welfare: Table = Table(
    "welfare",
    metadata_obj,
    Column("job_uid", BigInteger, ForeignKey("dim_job.id", ondelete="CASCADE"), primary_key=True),
    Column("tags", JSON, comment="福利標籤 List"),
    Column("legal_tags", JSON, comment="法定標籤 List"),
    Column("welfare_description", Text),
    # 定義 MySQL 特定 JSON 多值索引 (需配合 DB 版本)
    Index("idx_welfare_tags", text("(CAST(tags AS CHAR(50) ARRAY))")),
    Index("idx_legal_tags", text("(CAST(legal_tags AS CHAR(50) ARRAY))")),
    comment="職缺福利資訊表",
)

# ==========================================
# 5. Bridge Tables (Many-to-Many Associations)
# ==========================================

# 技能表
bridge_skills: Table = Table(
    "bridge_skills",
    metadata_obj,
    Column("job_uid", BigInteger, ForeignKey("dim_job.id", ondelete="CASCADE"), primary_key=True),
    Column("skill_name", String(250), primary_key=True),  # 複合主鍵
    comment="職缺-技能關聯表",
)

# 專長表
bridge_specialties: Table = Table(
    "bridge_specialties",
    metadata_obj,
    Column("job_uid", BigInteger, ForeignKey("dim_job.id", ondelete="CASCADE"), primary_key=True),
    Column("specialty_name", String(250), primary_key=True),
    comment="職缺-專長關聯表",
)

# 科系表
bridge_major: Table = Table(
    "bridge_major",
    metadata_obj,
    Column("job_uid", BigInteger, ForeignKey("dim_job.id", ondelete="CASCADE"), primary_key=True),
    Column("major_name", String(50), primary_key=True),
    comment="職缺-科系要求關聯表",
)

# 職類表
bridge_category: Table = Table(
    "bridge_category",
    metadata_obj,
    Column("job_uid", BigInteger, ForeignKey("dim_job.id", ondelete="CASCADE"), primary_key=True),
    Column("category_name", String(100), primary_key=True),
    comment="職缺-職類關聯表",
)

# 語言表 (含屬性欄位)
bridge_language: Table = Table(
    "bridge_language",
    metadata_obj,
    Column("job_uid", BigInteger, ForeignKey("dim_job.id", ondelete="CASCADE"), primary_key=True),
    Column("language", String(50), primary_key=True),  # 複合主鍵
    # 關聯屬性 (Association Attributes)
    Column("listening", String(30)),
    Column("speaking", String(30)),
    Column("reading", String(30)),
    Column("writing", String(30)),
    comment="職缺-語言能力要求表",
)
