from types import MappingProxyType

from sqlalchemy import Column, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class US_Man_Industry_Ranking(Base):
    __tablename__ = "US_Man_Industry_Ranking"
    year = Column(Integer, primary_key=True)
    month = Column(Integer, primary_key=True)
    apparel_PMI = Column(Integer, nullable=False)
    chemical_PMI = Column(Integer, nullable=False)
    computer_electronics_PMI = Column(Integer, nullable=False)
    electrical_equipment_PMI = Column(Integer, nullable=False)
    fabricated_metal_PMI = Column(Integer, nullable=False)
    food_beverage_tobacco_PMI = Column(Integer, nullable=False)
    furniture_PMI = Column(Integer, nullable=False)
    machinery_PMI = Column(Integer, nullable=False)
    miscellaneous_PMI = Column(Integer, nullable=False)
    non_metallic_mineral_PMI = Column(Integer, nullable=False)
    paper_PMI = Column(Integer, nullable=False)
    petroleum_coal_PMI = Column(Integer, nullable=False)
    plastic_rubber_PMI = Column(Integer, nullable=False)
    metals_PMI = Column(Integer, nullable=False)
    printing_PMI = Column(Integer, nullable=False)
    textiles_PMI = Column(Integer, nullable=False)
    transportation_PMI = Column(Integer, nullable=False)
    wood_PMI = Column(Integer, nullable=False)
    apparel_NewOrders = Column(Integer, nullable=False)
    chemical_NewOrders = Column(Integer, nullable=False)
    computer_electronics_NewOrders = Column(Integer, nullable=False)
    electrical_equipment_NewOrders = Column(Integer, nullable=False)
    fabricated_metal_NewOrders = Column(Integer, nullable=False)
    food_beverage_tobacco_NewOrders = Column(Integer, nullable=False)
    furniture_NewOrders = Column(Integer, nullable=False)
    machinery_NewOrders = Column(Integer, nullable=False)
    miscellaneous_NewOrders = Column(Integer, nullable=False)
    non_metallic_mineral_NewOrders = Column(Integer, nullable=False)
    paper_NewOrders = Column(Integer, nullable=False)
    petroleum_coal_NewOrders = Column(Integer, nullable=False)
    plastic_rubber_NewOrders = Column(Integer, nullable=False)
    metals_NewOrders = Column(Integer, nullable=False)
    printing_NewOrders = Column(Integer, nullable=False)
    textiles_NewOrders = Column(Integer, nullable=False)
    transportation_NewOrders = Column(Integer, nullable=False)
    wood_NewOrders = Column(Integer, nullable=False)

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
                "Apparel, Leather & Allied Products": "apparel_PMI",
                "Chemical Products": "chemical_PMI",
                "Computer & Electronic Products": "computer_electronics_PMI",
                "Electrical Equipment, Appliances & Components": "electrical_equipment_PMI",
                "Fabricated Metal Products": "fabricated_metal_PMI",
                "Food, Beverage & Tobacco Products": "food_beverage_tobacco_PMI",
                "Furniture & Related Products": "furniture_PMI",
                "Machinery": "machinery_PMI",
                "Miscellaneous Manufacturing": "miscellaneous_PMI",
                "Nonmetallic Mineral Products": "non_metallic_mineral_PMI",
                "Paper Products": "paper_PMI",
                "Petroleum & Coal Products": "petroleum_coal_PMI",
                "Plastics & Rubber Products": "plastic_rubber_PMI",
                "Primary Metals": "metals_PMI",
                "Printing & Related Support Activities": "printing_PMI",
                "Textile Mills": "textiles_PMI",
                "Transportation Equipment": "transportation_PMI",
                "Wood Products": "wood_PMI",
                "Apparel, Leather & Allied Products - New Orders": "apparel_NewOrders",
                "Chemical Products - New Orders": "chemical_NewOrders",
                "Computer & Electronic Products - New Orders": "computer_electronics_NewOrders",
                "Electrical Equipment, Appliances & Components - New Orders": "electrical_equipment_NewOrders",
                "Fabricated Metal Products - New Orders": "fabricated_metal_NewOrders",
                "Food, Beverage & Tobacco Products - New Orders": "food_beverage_tobacco_NewOrders",
                "Furniture & Related Products - New Orders": "furniture_NewOrders",
                "Machinery - New Orders": "machinery_NewOrders",
                "Miscellaneous Manufacturing - New Orders": "miscellaneous_NewOrders",
                "Nonmetallic Mineral Products - New Orders": "non_metallic_mineral_NewOrders",
                "Paper Products - New Orders": "paper_NewOrders",
                "Petroleum & Coal Products - New Orders": "petroleum_coal_NewOrders",
                "Plastics & Rubber Products - New Orders": "plastic_rubber_NewOrders",
                "Primary Metals - New Orders": "metals_NewOrders",
                "Printing & Related Support Activities - New Orders": "printing_NewOrders",
                "Textile Mills - New Orders": "textiles_NewOrders",
                "Transportation Equipment - New Orders": "transportation_NewOrders",
                "Wood Products - New Orders": "wood_NewOrders",
            }
        )
