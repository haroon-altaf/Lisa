from sqlalchemy import Column, Integer, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class GICS_Sectors(Base):
    __tablename__ = "GICS_Sectors"
    id = Column(Integer, primary_key=True, autoincrement=True)
    sector = Column(Text, nullable=False, unique=True)

    @classmethod
    def name(cls):
        return cls.__tablename__

    @classmethod
    def columns(cls):
        return [c.name for c in cls.__table__.columns]


# Relationships for navigation
industries = relationship("GICS_Industries", back_populates="sector", cascade="all, delete")
