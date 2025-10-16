from types import MappingProxyType

from sqlalchemy import Column, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class US_Ser_Industry_Ranking(Base):
    __tablename__ = "US_Ser_Industry_Ranking"
    year = Column(Integer, primary_key=True)
    month = Column(Integer, primary_key=True)
    accommodation_food_PMI = Column(Integer, nullable=False)
    agriculture_forestry_PMI = Column(Integer, nullable=False)
    arts_entertainment_PMI = Column(Integer, nullable=False)
    construction_PMI = Column(Integer, nullable=False)
    education_PMI = Column(Integer, nullable=False)
    finance_insurance_PMI = Column(Integer, nullable=False)
    healthcare_PMI = Column(Integer, nullable=False)
    information_PMI = Column(Integer, nullable=False)
    company_management_PMI = Column(Integer, nullable=False)
    mining_PMI = Column(Integer, nullable=False)
    other_PMI = Column(Integer, nullable=False)
    technical_services_PMI = Column(Integer, nullable=False)
    public_admin_PMI = Column(Integer, nullable=False)
    real_estate_PMI = Column(Integer, nullable=False)
    retail_trade_PMI = Column(Integer, nullable=False)
    transportation_warehousing_PMI = Column(Integer, nullable=False)
    utilities_PMI = Column(Integer, nullable=False)
    wholesale_trade_PMI = Column(Integer, nullable=False)
    accommodation_food_BusinessActivity = Column(Integer, nullable=False)
    agriculture_forestry_BusinessActivity = Column(Integer, nullable=False)
    arts_entertainment_BusinessActivity = Column(Integer, nullable=False)
    construction_BusinessActivity = Column(Integer, nullable=False)
    education_BusinessActivity = Column(Integer, nullable=False)
    finance_insurance_BusinessActivity = Column(Integer, nullable=False)
    healthcare_BusinessActivity = Column(Integer, nullable=False)
    information_BusinessActivity = Column(Integer, nullable=False)
    company_management_BusinessActivity = Column(Integer, nullable=False)
    mining_BusinessActivity = Column(Integer, nullable=False)
    other_BusinessActivity = Column(Integer, nullable=False)
    technical_services_BusinessActivity = Column(Integer, nullable=False)
    public_admin_BusinessActivity = Column(Integer, nullable=False)
    real_estate_BusinessActivity = Column(Integer, nullable=False)
    retail_trade_BusinessActivity = Column(Integer, nullable=False)
    transportation_warehousing_BusinessActivity = Column(Integer, nullable=False)
    utilities_BusinessActivity = Column(Integer, nullable=False)
    wholesale_trade_BusinessActivity = Column(Integer, nullable=False)

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
                "Year": "year",
                "Month": "month",
                "Accommodation & Food Services": "accommodation_food_PMI",
                "Agriculture, Forestry, Fishing & Hunting": "agriculture_forestry_PMI",
                "Arts, Entertainment & Recreation": "arts_entertainment_PMI",
                "Construction": "construction_PMI",
                "Educational Services": "education_PMI",
                "Finance & Insurance": "finance_insurance_PMI",
                "Health Care & Social Assistance": "healthcare_PMI",
                "Information": "information_PMI",
                "Management of Companies & Support Services": "company_management_PMI",
                "Mining": "mining_PMI",
                "Other Services": "other_PMI",
                "Professional, Scientific & Technical Services": "technical_services_PMI",
                "Public Administration": "public_admin_PMI",
                "Real Estate, Rental & Leasing": "real_estate_PMI",
                "Retail Trade": "retail_trade_PMI",
                "Transportation & Warehousing": "transportation_warehousing_PMI",
                "Utilities": "utilities_PMI",
                "Wholesale Trade": "wholesale_trade_PMI",
                "Accommodation & Food Services - Business Activity": "accommodation_food_BusinessActivity",
                "Agriculture, Forestry, Fishing & Hunting - Business Activity": "agriculture_forestry_BusinessActivity",
                "Arts, Entertainment & Recreation - Business Activity": "arts_entertainment_BusinessActivity",
                "Construction - Business Activity": "construction_BusinessActivity",
                "Educational Services - Business Activity": "education_BusinessActivity",
                "Finance & Insurance - Business Activity": "finance_insurance_BusinessActivity",
                "Health Care & Social Assistance - Business Activity": "healthcare_BusinessActivity",
                "Information - Business Activity": "information_BusinessActivity",
                "Management of Companies & Support Services - Business Activity": "company_management_BusinessActivity",
                "Mining - Business Activity": "mining_BusinessActivity",
                "Other Services - Business Activity": "other_BusinessActivity",
                "Professional, Scientific & Technical Services - Business Activity": "technical_services_BusinessActivity",
                "Public Administration - Business Activity": "public_admin_BusinessActivity",
                "Real Estate, Rental & Leasing - Business Activity": "real_estate_BusinessActivity",
                "Retail Trade - Business Activity": "retail_trade_BusinessActivity",
                "Transportation & Warehousing - Business Activity": "transportation_warehousing_BusinessActivity",
                "Utilities - Business Activity": "utilities_BusinessActivity",
                "Wholesale Trade - Business Activity": "wholesale_trade_BusinessActivity",
            }
        )
