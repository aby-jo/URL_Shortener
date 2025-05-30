from database import Base 
from sqlalchemy import Column,Integer,String,DateTime,func,ForeignKey
from sqlalchemy.orm import relationship

class ShortURL(Base):
    __tablename__='short_url'
    uuid=Column(Integer,primary_key=True,index=True,autoincrement=True)
    original_url=Column(String,nullable=False)
    short_code=Column(String,unique=True,nullable=False,index=True)
    created_at=Column(DateTime(timezone=True),server_default=func.now())
    visit_count=Column(Integer,default=0)
    access_log=relationship("AccessLog",back_populates="short_url")
class AccessLog(Base):
    __tablename__="access_log"
    uuid=Column(Integer,primary_key=True,index=True,autoincrement=True)
    short_code=Column(String,ForeignKey('short_url.short_code'),nullable=False,index=True)
    time_stamp=Column(DateTime(timezone=True),server_default=func.now())
    short_url=relationship("ShortURL",back_populates="access_log")