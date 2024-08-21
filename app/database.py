from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pymysql
import app.config as config

pymysql.install_as_MySQLdb()

engine = create_engine(f'mysql+mysqldb://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}/{config.DB_NAME}', pool_recycle=3600)
Session = sessionmaker(bind=engine)
