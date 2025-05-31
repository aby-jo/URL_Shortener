from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

sqlite_file_name = "./data.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

Base = declarative_base()

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
