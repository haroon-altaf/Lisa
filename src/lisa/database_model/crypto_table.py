from types import MappingProxyType

from sqlalchemy import REAL, Column, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Crypto(Base):
    __tablename__ = "Crypto"
    item = Column(Text, primary_key=True)
    category = Column(Text, nullable=False)
    price = Column(REAL)
    day_pct = Column(REAL)
    weekly_pct = Column(REAL)
    monthly_pct = Column(REAL)
    ytd_pct = Column(REAL)
    yoy_pct = Column(REAL)
    market_cap_m_usd = Column(REAL)
    date = Column(Text)

    @classmethod
    def name(cls):
        return cls.__tablename__

    @classmethod
    def columns(cls):
        return [c.name for c in cls.__table__.columns]

    @staticmethod
    def column_map():
        return MappingProxyType(
            {
                "Item": "item",
                "Category": "category",
                "Price": "price",
                "Day %": "day_pct",
                "Weekly %": "weekly_pct",
                "Monthly %": "monthly_pct",
                "YTD %": "ytd_pct",
                "YoY %": "yoy_pct",
                "Market Cap (m USD)": "market_cap_m_usd",
                "Date": "date",
            }
        )
