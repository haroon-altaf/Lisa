from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class GICS_Industries(Base):
    __tablename__ = "GICS_Industries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    industry = Column(Text, nullable=False, unique=True)
    sector_id = Column(Integer, ForeignKey("GICS_Sectors.id", ondelete="CASCADE"), nullable=False)

    @classmethod
    def name(cls):
        return cls.__tablename__

    @classmethod
    def columns(cls):
        return [c.name for c in cls.__table__.columns]


# Relationships for navigation
sector = relationship("GICS_Sectors", back_populates="industries")
