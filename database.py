from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

sqlite_file_name="./data.db"
sqlite_url=f'sqlite:///{sqlite_file_name}'
connect_args = {"check_same_thread": False}
engine=create_engine(sqlite_url,connect_args=connect_args)

Base=declarative_base()

SessionLocal=sessionmaker(bind=engine,autocommit=False,autoflush=False)