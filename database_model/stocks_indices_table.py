from sqlalchemy import Column, Text, REAL
from types import MappingProxyType
from sqlalchemy.orm import declarative_base
Base = declarative_base()

class Stock_Indices(Base):
    __tablename__ = 'Stock_Indices'
    item = Column(Text, primary_key=True)
    category = Column(Text, nullable=False)
    price = Column(REAL)
    day_pct = Column(REAL)
    weekly_pct = Column(REAL)
    monthly_pct = Column(REAL)
    ytd_pct = Column(REAL)
    yoy_pct = Column(REAL)
    date = Column(Text)
                
    @classmethod
    def name(cls):
        return cls.__tablename__

    @classmethod
    def columns(cls):
        return [c.name for c in cls.__table__.columns]

    @staticmethod
    def column_map():

        return MappingProxyType({
            'Item': 'item',
            'Category': 'category',
            'Price': 'price',
            'Day %': 'day_pct',
            'Weekly %': 'weekly_pct',
            'Monthly %': 'monthly_pct',
            'YTD %': 'ytd_pct',
            'YoY %': 'yoy_pct',
            'Date': 'date'
        })