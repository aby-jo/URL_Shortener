from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import model

test_sqlite_file_name = "./test_data.db"
test_sqlite_url = f"sqlite:///{test_sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(test_sqlite_url, connect_args=connect_args)


TestSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
model.Base.metadata.create_all(bind=engine)
