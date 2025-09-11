from sqlalchemy import Column, Text
from sqlalchemy.orm import declarative_base
Base = declarative_base()

class Finviz_Stocks_Description(Base):
    __tablename__ = 'Finviz_Stocks_Description'
    ticker = Column(Text, primary_key=True)
    description = Column(Text)
        
    @classmethod
    def name(cls):
        return cls.__tablename__

    @classmethod
    def columns(cls):
        return [c.name for c in cls.__table__.columns]