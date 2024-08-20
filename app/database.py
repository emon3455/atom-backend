from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pymysql
import app.config as config

pymysql.install_as_MySQLdb()

engine = create_engine(f'mysql+mysqldb://{config.db_user}:{config.db_password}@{config.host}/{config.db_name}', pool_recycle=3600)
Session = sessionmaker(bind=engine)
