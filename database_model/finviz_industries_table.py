from sqlalchemy import Column, Integer, REAL, ForeignKey
from types import MappingProxyType
from sqlalchemy.orm import declarative_base, relationship
Base = declarative_base()

class Finviz_Industries(Base):
    __tablename__ = 'Finviz_Industries'
    gics_industry_id = Column(Integer, ForeignKey('GICS_Industries.id'), primary_key=True)
    market_cap_m_usd = Column(REAL)
    p_e = Column(REAL)
    fwd_p_e = Column(REAL)
    peg = Column(REAL)
    p_s = Column(REAL)
    p_b = Column(REAL)
    p_c = Column(REAL)
    p_fcf = Column(REAL)
    dividend_pct = Column(REAL)
    eps_past_5y_pct = Column(REAL)
    eps_next_5y_pct = Column(REAL)
    sales_past_5y_pct = Column(REAL)
    float_short_pct = Column(REAL)
    perf_week_pct = Column(REAL)
    perf_month_pct = Column(REAL)
    perf_quart_pct = Column(REAL)
    perf_half_pct = Column(REAL)
    perf_year_pct = Column(REAL)
    perf_ytd_pct = Column(REAL)
    recom = Column(REAL)
    avg_volume_m_usd = Column(REAL)
    rel_volume = Column(REAL)
    change_pct = Column(REAL)
    volume_m_usd = Column(REAL)
    stocks = Column(Integer)
    
    @classmethod
    def name(cls):
        return cls.__tablename__

    @classmethod
    def columns(cls):
        return [c.name for c in cls.__table__.columns]

    @staticmethod
    def column_map():

        return MappingProxyType({
            'Industry' : 'gics_industry_id',
            'Market Cap (m USD)' : 'market_cap_m_usd',
            'P/E' : 'p_e',
            'Fwd P/E' : 'fwd_p_e',
            'PEG' : 'peg',
            'P/S' : 'p_s',
            'P/B' : 'p_b',
            'P/C' : 'p_c',
            'P/FCF' : 'p_fcf',
            'Dividend (%)' : 'dividend_pct',
            'EPS past 5Y (%)' : 'eps_past_5y_pct',
            'EPS next 5Y (%)' : 'eps_next_5y_pct',
            'Sales past 5Y (%)' : 'sales_past_5y_pct',
            'Float Short (%)' : 'float_short_pct',
            'Perf Week (%)' : 'perf_week_pct',
            'Perf Month (%)' : 'perf_month_pct',
            'Perf Quart (%)' : 'perf_quart_pct',
            'Perf Half (%)' : 'perf_half_pct',
            'Perf Year (%)' : 'perf_year_pct',
            'Perf YTD (%)' : 'perf_ytd_pct',
            'Recom' : 'recom',
            'Avg Volume (m USD)' : 'avg_volume_m_usd',
            'Rel Volume' : 'rel_volume',
            'Change (%)' : 'change_pct',
            'Volume (m USD)' : 'volume_m_usd',
            'Stocks' : 'stocks'
        })

# Relationships for navigation
industries = relationship("GICS_Industries")