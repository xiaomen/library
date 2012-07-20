from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('mysql://', echo=True, pool_recycle=3600)

Base = declarative_base()
class SearchRecord(Base):
    __tablename__ = 'search_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer, nullable=False)
    record = Column(String(1024), nullable=False)
    time = Column(DateTime, nullable=False)
    
    def __init__(self, uid, record, time):
        self.uid = uid
        self.record = record
        self.time = time

    def __repr__(self):
        return "<SearchRecord(%s, %s, %s)>" % (self.id, self.uid, self.record, self.time)

metadata = Base.metadata
metadata.create_all(engine)
