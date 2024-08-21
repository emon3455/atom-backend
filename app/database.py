from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pymysql

pymysql.install_as_MySQLdb()

engine = create_engine(f'mysql+mysqldb://emon:53z5H6qs$@72.167.50.253/locations', pool_recycle=3600)
Session = sessionmaker(bind=engine)
