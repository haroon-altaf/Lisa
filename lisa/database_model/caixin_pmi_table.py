from types import MappingProxyType

from sqlalchemy import REAL, Column, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Caixin_PMI(Base):
    __tablename__ = "Caixin_PMI"
    year = Column(Integer, primary_key=True)
    month = Column(Integer, primary_key=True)
    manufacturing_pmi = Column(REAL)
    services_pmi = Column(REAL)

    @classmethod
    def name(cls):
        return cls.__tablename__

    @classmethod
    def columns(cls):
        return [c.name for c in cls.__table__.columns]

    @staticmethod
    def column_map():
        return MappingProxyType(
            {"Year": "year", "Month": "month", "Manufacturing PMI": "manufacturing_pmi", "Services PMI": "services_pmi"}
        )
