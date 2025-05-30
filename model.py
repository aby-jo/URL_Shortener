from database import Base 
from sqlalchemy import Column,Integer,String,DateTime,func

class ShortURL(Base):
    __tablename__='short_url'
    uuid=Column(Integer,primary_key=True,index=True,autoincrement=True)
    original_url=Column(String,nullable=False)
    short_code=Column(String,unique=True,nullable=False,index=True)
    created_at=Column(DateTime(timezone=True),server_default=func.now())
    visit_count=Column(Integer,default=0)