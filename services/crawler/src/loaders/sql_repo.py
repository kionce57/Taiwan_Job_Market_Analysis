import sqlalchemy as sa
import os
from src.interfaces.interfaces import SilverJobRepository
from dotenv import load_dotenv
# from ...config.mysql_schema import 

load_dotenv()

class tjma_database(SilverJobRepository):
    # sql
    
    def __init__(self) -> None:
        # conn str: dialect+driver://username:password@host:port/database
        driver = os.getenv("MySQLDriver")
        username = os.getenv("MySQLUser")
        password = os.getenv("MySQLPassword")
        host = os.getenv("MySQLHost")
        port = os.getenv("MySQLPort")
        database = os.getenv("MySQLDatabase")
        self.conn_str = f"{driver}://{username}:{password}@{host}:{port}/{database}"
        self.engine = sa.create_engine(self.conn_str)
        self.conn = self.engine.connect()

    def select_stage(self):

    def insert_stage(self):
        
    def update_stage(self):
        