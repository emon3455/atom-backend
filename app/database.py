from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')

pymysql.install_as_MySQLdb()


engine = create_engine(f'mysql+mysqldb://{db_user}:{db_password}@{db_host}/{db_name}', pool_recycle=3600)
Session = sessionmaker(bind=engine)
