from sqlalchemy import Column, Integer, REAL
from types import MappingProxyType
from sqlalchemy.orm import declarative_base
Base = declarative_base()

class US_Consumers(Base):
    __tablename__ = 'US_Consumers'
    year = Column(Integer, primary_key=True)
    month = Column(Integer, primary_key=True)
    consumer_sentiment_index = Column(REAL)
    current_conditions_index = Column(REAL)
    expectations_index = Column(REAL)
                
    @classmethod
    def name(cls):
        return cls.__tablename__

    @classmethod
    def columns(cls):
        return [c.name for c in cls.__table__.columns]

    @staticmethod
    def column_map():

        return MappingProxyType({
            'Year': 'year',
            'Month': 'month',
            'Index': 'consumer_sentiment_index',
            'Current Index': 'current_conditions_index',
            'Expected Index': 'expectations_index'
        })