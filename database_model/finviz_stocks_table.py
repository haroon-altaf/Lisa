from sqlalchemy import Column, Integer, REAL, Text,ForeignKey
from types import MappingProxyType
from sqlalchemy.orm import declarative_base, relationship
Base = declarative_base()

class Finviz_Stocks(Base):
    __tablename__ = 'Finviz_Stocks'
    ticker = Column(Text, primary_key=True)
    company = Column(Text, nullable=False)
    gics_industry_id = Column(Integer, ForeignKey('GICS_Industries.id'), nullable=False)
    gics_sector_id = Column(Integer, ForeignKey('GICS_Sectors.id'), nullable=False)
    index = Column(Text)
    country = Column(Text)
    exchange = Column(Text)
    market_cap_m_usd = Column(REAL)
    p_e = Column(REAL)
    fwd_p_e = Column(REAL)
    peg = Column(REAL)
    p_s = Column(REAL)
    p_b = Column(REAL)
    p_c = Column(REAL)
    p_fcf = Column(REAL)
    book_sh = Column(REAL)
    cash_sh = Column(REAL)
    dividend = Column(REAL)
    dividend_pct = Column(REAL)
    dividend_ttm = Column(REAL)
    dividend_ex_date = Column(Text)
    payout_ratio_pct = Column(REAL)
    eps = Column(REAL)
    eps_next_q = Column(REAL)
    eps_this_y_pct = Column(REAL)
    eps_next_y_pct = Column(REAL)
    eps_past_5y_pct = Column(REAL)
    eps_next_5y_pct = Column(REAL)
    sales_past_5y_pct = Column(REAL)
    sales_q_q_pct = Column(REAL)
    eps_q_q_pct = Column(REAL)
    eps_yoy_ttm_pct = Column(REAL)
    sales_yoy_ttm_pct = Column(REAL)
    sales_m_usd = Column(REAL)
    income_m_usd = Column(REAL)
    eps_surprise_pct = Column(REAL)
    revenue_surprise_pct = Column(REAL)
    outstanding_m_usd = Column(REAL)
    float_m_usd = Column(REAL)
    float_pct = Column(REAL)
    insider_own_pct = Column(REAL)
    insider_trans_pct = Column(REAL)
    inst_own_pct = Column(REAL)
    inst_trans_pct = Column(REAL)
    short_float_pct = Column(REAL)
    short_ratio = Column(REAL)
    short_interest_m_usd = Column(REAL)
    roa_pct = Column(REAL)
    roe_pct = Column(REAL)
    roic_pct = Column(REAL)
    curr_r = Column(REAL)
    quick_r = Column(REAL)
    ltdebt_eq = Column(REAL)
    debt_eq = Column(REAL)
    gross_m_pct = Column(REAL)
    oper_m_pct = Column(REAL)
    profit_m_pct = Column(REAL)
    perf_week_pct = Column(REAL)
    perf_month_pct = Column(REAL)
    perf_quart_pct = Column(REAL)
    perf_half_pct = Column(REAL)
    perf_year_pct = Column(REAL)
    perf_ytd_pct = Column(REAL)
    beta = Column(REAL)
    atr = Column(REAL)
    volatility_w_pct = Column(REAL)
    volatility_m_pct = Column(REAL)
    sma20_pct = Column(REAL)
    sma50_pct = Column(REAL)
    sma200_pct = Column(REAL)
    _50d_high_pct = Column('50d_high_pct',REAL)
    _50d_low_pct = Column('50d_low_pct', REAL)
    _52w_high_pct = Column('52w_high_pct', REAL)
    _52w_low_pct = Column('52w_low_pct', REAL)
    _52w_range = Column('52w_range', Text)
    all_time_high_pct = Column(REAL)
    all_time_low_pct = Column(REAL)
    rsi = Column(REAL)
    earnings = Column(Text)
    ipo_date = Column(Text)
    optionable = Column(Text)
    shortable = Column(Text)
    employees = Column(Integer)
    change_from_open_pct = Column(REAL)
    gap_pct = Column(REAL)
    recom = Column(REAL)
    avg_volume_m_usd = Column(REAL)
    rel_volume = Column(REAL)
    volume = Column(REAL)
    target_price = Column(REAL)
    prev_close = Column(REAL)
    open = Column(REAL)
    high = Column(REAL)
    low = Column(REAL)
    price = Column(REAL)
    change_pct = Column(REAL)
            
    @classmethod
    def name(cls):
        return cls.__tablename__

    @classmethod
    def columns(cls):
        return [c.name for c in cls.__table__.columns]

    @staticmethod
    def column_map():

        return MappingProxyType({
            'Ticker' : 'ticker',
            'Company' : 'company',
            'Index' : 'index',
            'Sector' : 'gics_sector_id',
            'Industry' : 'gics_industry_id',
            'Country' : 'country',
            'Exchange' : 'exchange',
            'Market Cap (m USD)' : 'market_cap_m_usd',
            'P/E' : 'p_e',
            'Fwd P/E' : 'fwd_p_e',
            'PEG' : 'peg',
            'P/S' : 'p_s',
            'P/B' : 'p_b',
            'P/C' : 'p_c',
            'P/FCF' : 'p_fcf',
            'Book/sh' : 'book_sh',
            'Cash/sh' : 'cash_sh',
            'Dividend' : 'dividend',
            'Dividend (%)' : 'dividend_pct',
            'Dividend TTM' : 'dividend_ttm',
            'Dividend Ex Date' : 'dividend_ex_date',
            'Payout Ratio (%)' : 'payout_ratio_pct',
            'EPS' : 'eps',
            'EPS next Q' : 'eps_next_q',
            'EPS This Y (%)' : 'eps_this_y_pct',
            'EPS Next Y (%)' : 'eps_next_y_pct',
            'EPS Past 5Y (%)' : 'eps_past_5y_pct',
            'EPS Next 5Y (%)' : 'eps_next_5y_pct',
            'Sales Past 5Y (%)' : 'sales_past_5y_pct',
            'Sales Q/Q (%)' : 'sales_q_q_pct',
            'EPS Q/Q (%)' : 'eps_q_q_pct',
            'EPS YoY TTM (%)' : 'eps_yoy_ttm_pct',
            'Sales YoY TTM (%)' : 'sales_yoy_ttm_pct',
            'Sales (m USD)' : 'sales_m_usd',
            'Income (m USD)' : 'income_m_usd',
            'EPS Surprise (%)' : 'eps_surprise_pct',
            'Revenue Surprise (%)' : 'revenue_surprise_pct',
            'Outstanding (m USD)' : 'outstanding_m_usd',
            'Float (m USD)' : 'float_m_usd',
            'Float %' : 'float_pct',
            'Insider Own (%)' : 'insider_own_pct',
            'Insider Trans (%)' : 'insider_trans_pct',
            'Inst Own (%)' : 'inst_own_pct',
            'Inst Trans (%)' : 'inst_trans_pct',
            'Short Float (%)' : 'short_float_pct',
            'Short Ratio' : 'short_ratio',
            'Short Interest (m USD)' : 'short_interest_m_usd',
            'ROA (%)' : 'roa_pct',
            'ROE (%)' : 'roe_pct',
            'ROIC (%)' : 'roic_pct',
            'Curr R' : 'curr_r',
            'Quick R' : 'quick_r',
            'LTDebt/Eq' : 'ltdebt_eq',
            'Debt/Eq' : 'debt_eq',
            'Gross M (%)' : 'gross_m_pct',
            'Oper M (%)' : 'oper_m_pct',
            'Profit M (%)' : 'profit_m_pct',
            'Perf Week (%)' : 'perf_week_pct',
            'Perf Month (%)' : 'perf_month_pct',
            'Perf Quart (%)' : 'perf_quart_pct',
            'Perf Half (%)' : 'perf_half_pct',
            'Perf Year (%)' : 'perf_year_pct',
            'Perf YTD (%)' : 'perf_ytd_pct',
            'Beta' : 'beta',
            'ATR' : 'atr',
            'Volatility W (%)' : 'volatility_w_pct',
            'Volatility M (%)' : 'volatility_m_pct',
            'SMA20 (%)' : 'sma20_pct',
            'SMA50 (%)' : 'sma50_pct',
            'SMA200 (%)' : 'sma200_pct',
            '50D High (%)' : '50d_high_pct',
            '50D Low (%)' : '50d_low_pct',
            '52W High (%)' : '52w_high_pct',
            '52W Low (%)' : '52w_low_pct',
            '52W Range' : '52w_range',
            'All-Time High (%)' : 'all_time_high_pct',
            'All-Time Low (%)' : 'all_time_low_pct',
            'RSI' : 'rsi',
            'Earnings' : 'earnings',
            'IPO Date' : 'ipo_date',
            'Optionable' : 'optionable',
            'Shortable' : 'shortable',
            'Employees' : 'employees',
            'Change from Open (%)' : 'change_from_open_pct',
            'Gap (%)' : 'gap_pct',
            'Recom' : 'recom',
            'Avg Volume (m USD)' : 'avg_volume_m_usd',
            'Rel Volume' : 'rel_volume',
            'Volume' : 'volume',
            'Target Price' : 'target_price',
            'Prev Close' : 'prev_close',
            'Open' : 'open',
            'High' : 'high',
            'Low' : 'low',
            'Price' : 'price',
            'Change (%)' : 'change_pct'
        })
    
# Relationships for navigation
industries = relationship('GICS_Industries')
sectors = relationship('GICS_Sectors')