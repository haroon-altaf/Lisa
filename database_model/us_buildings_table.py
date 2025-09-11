from sqlalchemy import Column, Integer
from types import MappingProxyType
from sqlalchemy.orm import declarative_base
Base = declarative_base()

class US_Buildings(Base):
    __tablename__ = 'US_Buildings'
    year = Column(Integer, primary_key=True)
    month = Column(Integer, primary_key=True)
    permits = Column(Integer)
    authorized = Column(Integer)
    starts = Column(Integer)
    under_construction = Column(Integer)
    completions = Column(Integer)
                
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
            'Permits': 'permits',
            'Authorized': 'authorized',
            'Starts': 'starts',
            'Under Construction': 'under_construction',
            'Completions': 'completions'
        })