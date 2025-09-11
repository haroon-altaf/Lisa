from sqlalchemy import Column, Text, REAL
from types import MappingProxyType
from sqlalchemy.orm import declarative_base
Base = declarative_base()

class Commodities(Base):
    __tablename__ = 'Commodities'
    item = Column(Text, primary_key=True)
    category = Column(Text, nullable=False)
    unit = Column(Text)
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
            'Unit': 'unit',
            'Price': 'price',
            'Day %': 'day_pct',
            'Weekly %': 'weekly_pct',
            'Monthly %': 'monthly_pct',
            'YTD %': 'ytd_pct',
            'YoY %': 'yoy_pct',
            'Date': 'date'
        })