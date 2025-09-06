# This file contains static data and configurable parameters that are used in other program files.
from pathlib import Path
from dataclasses import dataclass

@dataclass(frozen=True)
class MONTHS:
    january, jan = 1, 1
    february, feb = 2, 2
    march, mar = 3, 3
    april, apr = 4, 4
    may = 5
    june, jun = 6, 6
    july, jul = 7, 7
    august, aug = 8, 8
    september, sep = 9, 9
    october, oct = 10, 10    
    november, nov = 11, 11
    december, dec = 12, 12

@dataclass(frozen=True)
class URL:
    us_man_pmi = "https://www.ismworld.org/supply-management-news-and-reports/reports/ism-report-on-business/pmi/"
    us_ser_pmi = "https://www.ismworld.org/supply-management-news-and-reports/reports/ism-report-on-business/services/"
    us_cons_index = "https://www.sca.isr.umich.edu/files/tbcics.csv"
    us_cons_comp = "https://www.sca.isr.umich.edu/files/tbciccice.csv"
    us_buil_permit = "https://www.census.gov/construction/nrc/xls/permits_cust.xlsx"
    us_buil_auth = "https://www.census.gov/construction/nrc/xls/authnot_cust.xlsx"
    us_buil_start = "https://www.census.gov/construction/nrc/xls/starts_cust.xlsx"
    us_buil_construct = "https://www.census.gov/construction/nrc/xls/under_cust.xlsx"
    us_buil_complete = "https://www.census.gov/construction/nrc/xls/comps_cust.xlsx"
    euro = "https://economy-finance.ec.europa.eu/economic-forecast-and-surveys/business-and-consumer-surveys/download-business-and-consumer-survey-data/time-series_en"
    caixin_man_pmi = "https://tradingeconomics.com/china/manufacturing-pmi"
    caixin_ser_pmi = "https://tradingeconomics.com/china/services-pmi"
    finviz_screen = "https://finviz.com/screener.ashx?v=151&f=ind_stocksonly&o=ticker&c="
    finviz_stock = "https://finviz.com/quote.ashx"
    finviz_indu = "https://finviz.com/groups.ashx?g=industry&v=152&o=name&c=1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26"
    commodities = "https://tradingeconomics.com/commodities"
    stocks = "https://tradingeconomics.com/stocks"
    bonds = "https://tradingeconomics.com/bonds"
    currencies = "https://tradingeconomics.com/currencies"
    crypto = "https://tradingeconomics.com/crypto"

@dataclass
class LOGGING_CONST:
    file_path = Path.cwd().joinpath('app.log')
    encoding = 'utf-8'
    console_level = 10
    file_level = 30
    console_formatter = '%(asctime)s | %(levelname)s | %(module)s | Line %(lineno)d | %(funcName)s | %(message)s'
    rotation_when = 'W0'
    rotation_interval = 1
    rotation_backups = 10

@dataclass(frozen=True)
class DB_CONST:
    path = './Leading Indicators and Stocks.db'
    exe_limit = 32766

@dataclass
class GET_REQ_CONST:
    timeout= 10
    max_retries= 3
    backoff_factor= 1.0
    session_renewal_interval= 1000
    ua_list= (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    )

@dataclass
class FINVIZ_CONST:
    screener_columns = (
        1, 2, 79, 3, 4, 5, 129, 6, 7, 8, 9, 10, 11, 12, 13, 73, 74, 75, 14, 130, 131, 15, 16, 77, 17, 18, 19, 20, 21, 23, 22, 132, 133,
        82, 78, 127, 128, 24, 25, 85, 26, 27, 28, 29, 30, 31, 84, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
        50, 51, 52, 53, 54, 55, 56, 57, 58, 134, 125, 126, 59, 68, 70, 80, 83, 76, 60, 61, 62, 63, 64, 67, 69, 81, 86, 87, 88, 65, 66
    )
    max_rows = 10000
    rows_per_page = 20

MAN_SECTORS = (
    "Apparel, Leather & Allied Products",
    "Chemical Products",
    "Computer & Electronic Products",
    "Electrical Equipment, Appliances & Components",
    "Fabricated Metal Products",
    "Food, Beverage & Tobacco Products",
    "Furniture & Related Products",
    "Machinery",
    "Miscellaneous Manufacturing",
    "Nonmetallic Mineral Products",
    "Paper Products",
    "Petroleum & Coal Products",
    "Plastics & Rubber Products",
    "Primary Metals",
    "Printing & Related Support Activities",
    "Textile Mills",
    "Transportation Equipment",
    "Wood Products"
)

SERV_SECTORS = (
    "Accommodation & Food Services",
    "Agriculture, Forestry, Fishing & Hunting",
    "Arts, Entertainment & Recreation",
    "Construction",
    "Educational Services",
    "Finance & Insurance",
    "Health Care & Social Assistance",
    "Information",
    "Management of Companies & Support Services",
    "Mining",
    "Other Services",
    "Professional, Scientific & Technical Services",
    "Public Administration",
    "Real Estate, Rental & Leasing",
    "Retail Trade",
    "Transportation & Warehousing",
    "Utilities",
    "Wholesale Trade"
)

DB_STRUCTURE = {
    'ConsumerSurvey': {
        'table': {
            'name': 'US_Consumers',
            'map': {
                'Year': 'year',
                'Month': 'month',
                'Index': 'consumer_sentiment_index',
                'Current Index': 'current_conditions_index',
                'Expected Index': 'expectations_index'
            }
        }
    },
    'ConstructionSurvey': {
        'table': {
            'name': 'US_Buildings',
            'map': {
                'Year': 'year',
                'Month': 'month',
                'Permits': 'permits',
                'Authorized': 'authorized',
                'Starts': 'starts',
                'Under Construction': 'under_construction',
                'Completions': 'completions'
            }
        }
    },
    'EuroSurvey': {
        'table':{ 
            'name': 'EU_Economic_Sentiment',
            'map': {
                'Year': 'year',
                'Month': 'month',
                'EU.INDU': 'EU_indu', 'EU.SERV': 'EU_serv', 'EU.CONS': 'EU_cons', 'EU.RETA': 'EU_reta', 'EU.BUIL': 'EU_buil', 'EU.ESI': 'EU_esi', 'EU.EEI': 'EU_eei',
                'EA.INDU': 'EA_indu', 'EA.SERV': 'EA_serv', 'EA.CONS': 'EA_cons', 'EA.RETA': 'EA_reta', 'EA.BUIL': 'EA_buil', 'EA.ESI': 'EA_esi', 'EA.EEI': 'EA_eei',
                'BE.INDU': 'BE_indu', 'BE.SERV': 'BE_serv', 'BE.CONS': 'BE_cons', 'BE.RETA': 'BE_reta', 'BE.BUIL': 'BE_buil', 'BE.ESI': 'BE_esi', 'BE.EEI': 'BE_eei',
                'BG.INDU': 'BG_indu', 'BG.SERV': 'BG_serv', 'BG.CONS': 'BG_cons', 'BG.RETA': 'BG_reta', 'BG.BUIL': 'BG_buil', 'BG.ESI': 'BG_esi', 'BG.EEI': 'BG_eei',
                'CZ.INDU': 'CZ_indu', 'CZ.SERV': 'CZ_serv', 'CZ.CONS': 'CZ_cons', 'CZ.RETA': 'CZ_reta', 'CZ.BUIL': 'CZ_buil', 'CZ.ESI': 'CZ_esi', 'CZ.EEI': 'CZ_eei',
                'DK.INDU': 'DK_indu', 'DK.SERV': 'DK_serv', 'DK.CONS': 'DK_cons', 'DK.RETA': 'DK_reta', 'DK.BUIL': 'DK_buil', 'DK.ESI': 'DK_esi', 'DK.EEI': 'DK_eei',
                'DE.INDU': 'DE_indu', 'DE.SERV': 'DE_serv', 'DE.CONS': 'DE_cons', 'DE.RETA': 'DE_reta', 'DE.BUIL': 'DE_buil', 'DE.ESI': 'DE_esi', 'DE.EEI': 'DE_eei',
                'EE.INDU': 'EE_indu', 'EE.SERV': 'EE_serv', 'EE.CONS': 'EE_cons', 'EE.RETA': 'EE_reta', 'EE.BUIL': 'EE_buil', 'EE.ESI': 'EE_esi', 'EE.EEI': 'EE_eei',
                'IE.INDU': 'IE_indu', 'IE.SERV': 'IE_serv', 'IE.CONS': 'IE_cons', 'IE.RETA': 'IE_reta', 'IE.BUIL': 'IE_buil', 'IE.ESI': 'IE_esi', 'IE.EEI': 'IE_eei',
                'EL.INDU': 'EL_indu', 'EL.SERV': 'EL_serv', 'EL.CONS': 'EL_cons', 'EL.RETA': 'EL_reta', 'EL.BUIL': 'EL_buil', 'EL.ESI': 'EL_esi', 'EL.EEI': 'EL_eei',
                'ES.INDU': 'ES_indu', 'ES.SERV': 'ES_serv', 'ES.CONS': 'ES_cons', 'ES.RETA': 'ES_reta', 'ES.BUIL': 'ES_buil', 'ES.ESI': 'ES_esi', 'ES.EEI': 'ES_eei',
                'FR.INDU': 'FR_indu', 'FR.SERV': 'FR_serv', 'FR.CONS': 'FR_cons', 'FR.RETA': 'FR_reta', 'FR.BUIL': 'FR_buil', 'FR.ESI': 'FR_esi', 'FR.EEI': 'FR_eei',
                'HR.INDU': 'HR_indu', 'HR.SERV': 'HR_serv', 'HR.CONS': 'HR_cons', 'HR.RETA': 'HR_reta', 'HR.BUIL': 'HR_buil', 'HR.ESI': 'HR_esi', 'HR.EEI': 'HR_eei',
                'IT.INDU': 'IT_indu', 'IT.SERV': 'IT_serv', 'IT.CONS': 'IT_cons', 'IT.RETA': 'IT_reta', 'IT.BUIL': 'IT_buil', 'IT.ESI': 'IT_esi', 'IT.EEI': 'IT_eei',
                'CY.INDU': 'CY_indu', 'CY.SERV': 'CY_serv', 'CY.CONS': 'CY_cons', 'CY.RETA': 'CY_reta', 'CY.BUIL': 'CY_buil', 'CY.ESI': 'CY_esi', 'CY.EEI': 'CY_eei',
                'LV.INDU': 'LV_indu', 'LV.SERV': 'LV_serv', 'LV.CONS': 'LV_cons', 'LV.RETA': 'LV_reta', 'LV.BUIL': 'LV_buil', 'LV.ESI': 'LV_esi', 'LV.EEI': 'LV_eei',
                'LT.INDU': 'LT_indu', 'LT.SERV': 'LT_serv', 'LT.CONS': 'LT_cons', 'LT.RETA': 'LT_reta', 'LT.BUIL': 'LT_buil', 'LT.ESI': 'LT_esi', 'LT.EEI': 'LT_eei',
                'LU.INDU': 'LU_indu', 'LU.SERV': 'LU_serv', 'LU.CONS': 'LU_cons', 'LU.RETA': 'LU_reta', 'LU.BUIL': 'LU_buil', 'LU.ESI': 'LU_esi', 'LU.EEI': 'LU_eei',
                'HU.INDU': 'HU_indu', 'HU.SERV': 'HU_serv', 'HU.CONS': 'HU_cons', 'HU.RETA': 'HU_reta', 'HU.BUIL': 'HU_buil', 'HU.ESI': 'HU_esi', 'HU.EEI': 'HU_eei',
                'MT.INDU': 'MT_indu', 'MT.SERV': 'MT_serv', 'MT.CONS': 'MT_cons', 'MT.RETA': 'MT_reta', 'MT.BUIL': 'MT_buil', 'MT.ESI': 'MT_esi', 'MT.EEI': 'MT_eei',
                'NL.INDU': 'NL_indu', 'NL.SERV': 'NL_serv', 'NL.CONS': 'NL_cons', 'NL.RETA': 'NL_reta', 'NL.BUIL': 'NL_buil', 'NL.ESI': 'NL_esi', 'NL.EEI': 'NL_eei',
                'AT.INDU': 'AT_indu', 'AT.SERV': 'AT_serv', 'AT.CONS': 'AT_cons', 'AT.RETA': 'AT_reta', 'AT.BUIL': 'AT_buil', 'AT.ESI': 'AT_esi', 'AT.EEI': 'AT_eei',
                'PL.INDU': 'PL_indu', 'PL.SERV': 'PL_serv', 'PL.CONS': 'PL_cons', 'PL.RETA': 'PL_reta', 'PL.BUIL': 'PL_buil', 'PL.ESI': 'PL_esi', 'PL.EEI': 'PL_eei',
                'PT.INDU': 'PT_indu', 'PT.SERV': 'PT_serv', 'PT.CONS': 'PT_cons', 'PT.RETA': 'PT_reta', 'PT.BUIL': 'PT_buil', 'PT.ESI': 'PT_esi', 'PT.EEI': 'PT_eei',
                'RO.INDU': 'RO_indu', 'RO.SERV': 'RO_serv', 'RO.CONS': 'RO_cons', 'RO.RETA': 'RO_reta', 'RO.BUIL': 'RO_buil', 'RO.ESI': 'RO_esi', 'RO.EEI': 'RO_eei',
                'SI.INDU': 'SI_indu', 'SI.SERV': 'SI_serv', 'SI.CONS': 'SI_cons', 'SI.RETA': 'SI_reta', 'SI.BUIL': 'SI_buil', 'SI.ESI': 'SI_esi', 'SI.EEI': 'SI_eei',
                'SK.INDU': 'SK_indu', 'SK.SERV': 'SK_serv', 'SK.CONS': 'SK_cons', 'SK.RETA': 'SK_reta', 'SK.BUIL': 'SK_buil', 'SK.ESI': 'SK_esi', 'SK.EEI': 'SK_eei',
                'FI.INDU': 'FI_indu', 'FI.SERV': 'FI_serv', 'FI.CONS': 'FI_cons', 'FI.RETA': 'FI_reta', 'FI.BUIL': 'FI_buil', 'FI.ESI': 'FI_esi', 'FI.EEI': 'FI_eei',
                'SE.INDU': 'SE_indu', 'SE.SERV': 'SE_serv', 'SE.CONS': 'SE_cons', 'SE.RETA': 'SE_reta', 'SE.BUIL': 'SE_buil', 'SE.ESI': 'SE_esi', 'SE.EEI': 'SE_eei',
                'UK.INDU': 'UK_indu', 'UK.SERV': 'UK_serv', 'UK.CONS': 'UK_cons', 'UK.RETA': 'UK_reta', 'UK.BUIL': 'UK_buil', 'UK.ESI': 'UK_esi', 'UK.EEI': 'UK_eei',
                'ME.INDU': 'ME_indu', 'ME.SERV': 'ME_serv', 'ME.CONS': 'ME_cons', 'ME.RETA': 'ME_reta', 'ME.BUIL': 'ME_buil', 'ME.ESI': 'ME_esi', 'ME.EEI': 'ME_eei',
                'MK.INDU': 'MK_indu', 'MK.SERV': 'MK_serv', 'MK.CONS': 'MK_cons', 'MK.RETA': 'MK_reta', 'MK.BUIL': 'MK_buil', 'MK.ESI': 'MK_esi', 'MK.EEI': 'MK_eei',
                'AL.INDU': 'AL_indu', 'AL.SERV': 'AL_serv', 'AL.CONS': 'AL_cons', 'AL.RETA': 'AL_reta', 'AL.BUIL': 'AL_buil', 'AL.ESI': 'AL_esi', 'AL.EEI': 'AL_eei',
                'RS.INDU': 'RS_indu', 'RS.SERV': 'RS_serv', 'RS.CONS': 'RS_cons', 'RS.RETA': 'RS_reta', 'RS.BUIL': 'RS_buil', 'RS.ESI': 'RS_esi', 'RS.EEI': 'RS_eei',
                'TR.INDU': 'TR_indu', 'TR.SERV': 'TR_serv', 'TR.CONS': 'TR_cons', 'TR.RETA': 'TR_reta', 'TR.BUIL': 'TR_buil', 'TR.ESI': 'TR_esi', 'TR.EEI': 'TR_eei',
            }
        }
    },
    'CaixinPmi': {
        'table':{ 
            'name': 'Caixin_PMI',
            'map': {
                'Year': 'year',
                'Month': 'month',
                'Manufacturing PMI': 'manufacturing_pmi',
                'Services PMI': 'services_pmi'
            }
        }
    },
    'Commodities': {
        'table': {
            'name': 'Commodities',
            'map': {
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
            }
        }
    },
    'Stocks': {
        'table': {
            'name': 'Stock_Indices',
            'map': {
                'Item': 'item',
                'Category': 'category',
                'Price': 'price',
                'Day %': 'day_pct',
                'Weekly %': 'weekly_pct',
                'Monthly %': 'monthly_pct',
                'YTD %': 'ytd_pct',
                'YoY %': 'yoy_pct',
                'Date': 'date'
            }
        }
    },
    'Bonds': {
        'table': {
            'name': 'Bonds',
            'map': {
                'Item': 'item',
                'Category': 'category',
                'Yield': 'yield',
                'Day %': 'day_pct',
                'Weekly %': 'weekly_pct',
                'Monthly %': 'monthly_pct',
                'YTD %': 'ytd_pct',
                'YoY %': 'yoy_pct',
                'Date': 'date'
            }
        }
    },
    'Currencies': {
        'table': {
            'name': 'Currencies',
            'map': {
                'Item': 'item',
                'Category': 'category',
                'Price': 'price',
                'Day %': 'day_pct',
                'Weekly %': 'weekly_pct',
                'Monthly %': 'monthly_pct',
                'YTD %': 'ytd_pct',
                'YoY %': 'yoy_pct',
                'Date': 'date'
            }
        }
    },
    'Crypto': {
        'table': {
            'name': 'Crypto',
            'map': {
                'Item': 'item',
                'Category': 'category',
                'Price': 'price',
                'Day %': 'day_pct',
                'Weekly %': 'weekly_pct',
                'Monthly %': 'monthly_pct',
                'YTD %': 'ytd_pct',
                'YoY %': 'yoy_pct',
                'Market Cap (m USD)': 'market_cap_m_usd',
                'Date': 'date'
            }
        }
    },
    'FinvizIndustries': {
        'table': {
            'name': 'Finviz_Industries',
            'map': {
                "Industry" : "gics_industry_id",
                "Market Cap (m USD)" : "market_cap_m_usd",
                "P/E" : "p_e",
                "Fwd P/E" : "fwd_p_e",
                "PEG" : "peg",
                "P/S" : "p_s",
                "P/B" : "p_b",
                "P/C" : "p_c",
                "P/FCF" : "p_fcf",
                "Dividend (%)" : "dividend_pct",
                "EPS past 5Y (%)" : "eps_past_5y_pct",
                "EPS next 5Y (%)" : "eps_next_5y_pct",
                "Sales past 5Y (%)" : "sales_past_5y_pct",
                "Float Short (%)" : "float_short_pct",
                "Perf Week (%)" : "perf_week_pct",
                "Perf Month (%)" : "perf_month_pct",
                "Perf Quart (%)" : "perf_quart_pct",
                "Perf Half (%)" : "perf_half_pct",
                "Perf Year (%)" : "perf_year_pct",
                "Perf YTD (%)" : "perf_ytd_pct",
                "Recom" : "recom",
                "Avg Volume (m USD)" : "avg_volume_m_usd",
                "Rel Volume" : "rel_volume",
                "Change (%)" : "change_pct",
                "Volume (m USD)" : "volume_m_usd",
                "Stocks" : "stocks"
            }
        }
    },
    'FinvizScreener': {
        'table': {
            'name': 'Finviz_Stocks',
            'map': {
                "Ticker" : "ticker",
                "Company" : "company",
                "Index" : "index",
                "Sector" : "gics_sector_id",
                "Industry" : "gics_industry_id",
                "Country" : "country",
                "Exchange" : "exchange",
                "Market Cap (m USD)" : "market_cap_m_usd",
                "P/E" : "p_e",
                "Fwd P/E" : "fwd_p_e",
                "PEG" : "peg",
                "P/S" : "p_s",
                "P/B" : "p_b",
                "P/C" : "p_c",
                "P/FCF" : "p_fcf",
                "Book/sh" : "book_sh",
                "Cash/sh" : "cash_sh",
                "Dividend" : "dividend",
                "Dividend (%)" : "dividend_pct",
                "Dividend TTM" : "dividend_ttm",
                "Dividend Ex Date" : "dividend_ex_date",
                "Payout Ratio (%)" : "payout_ratio_pct",
                "EPS" : "eps",
                "EPS next Q" : "eps_next_q",
                "EPS This Y (%)" : "eps_this_y_pct",
                "EPS Next Y (%)" : "eps_next_y_pct",
                "EPS Past 5Y (%)" : "eps_past_5y_pct",
                "EPS Next 5Y (%)" : "eps_next_5y_pct",
                "Sales Past 5Y (%)" : "sales_past_5y_pct",
                "Sales Q/Q (%)" : "sales_q_q_pct",
                "EPS Q/Q (%)" : "eps_q_q_pct",
                "EPS YoY TTM (%)" : "eps_yoy_ttm_pct",
                "Sales YoY TTM (%)" : "sales_yoy_ttm_pct",
                "Sales (m USD)" : "sales_m_usd",
                "Income (m USD)" : "income_m_usd",
                "EPS Surprise (%)" : "eps_surprise_pct",
                "Revenue Surprise (%)" : "revenue_surprise_pct",
                "Outstanding (m USD)" : "outstanding_m_usd",
                "Float (m USD)" : "float_m_usd",
                "Float %" : "float_pct",
                "Insider Own (%)" : "insider_own_pct",
                "Insider Trans (%)" : "insider_trans_pct",
                "Inst Own (%)" : "inst_own_pct",
                "Inst Trans (%)" : "inst_trans_pct",
                "Short Float (%)" : "short_float_pct",
                "Short Ratio" : "short_ratio",
                "Short Interest (m USD)" : "short_interest_m_usd",
                "ROA (%)" : "roa_pct",
                "ROE (%)" : "roe_pct",
                "ROIC (%)" : "roic_pct",
                "Curr R" : "curr_r",
                "Quick R" : "quick_r",
                "LTDebt/Eq" : "ltdebt_eq",
                "Debt/Eq" : "debt_eq",
                "Gross M (%)" : "gross_m_pct",
                "Oper M (%)" : "oper_m_pct",
                "Profit M (%)" : "profit_m_pct",
                "Perf Week (%)" : "perf_week_pct",
                "Perf Month (%)" : "perf_month_pct",
                "Perf Quart (%)" : "perf_quart_pct",
                "Perf Half (%)" : "perf_half_pct",
                "Perf Year (%)" : "perf_year_pct",
                "Perf YTD (%)" : "perf_ytd_pct",
                "Beta" : "beta",
                "ATR" : "atr",
                "Volatility W (%)" : "volatility_w_pct",
                "Volatility M (%)" : "volatility_m_pct",
                "SMA20 (%)" : "sma20_pct",
                "SMA50 (%)" : "sma50_pct",
                "SMA200 (%)" : "sma200_pct",
                "50D High (%)" : "50d_high_pct",
                "50D Low (%)" : "50d_low_pct",
                "52W High (%)" : "52w_high_pct",
                "52W Low (%)" : "52w_low_pct",
                "52W Range" : "52w_range",
                "All-Time High (%)" : "all-time_high_pct",
                "All-Time Low (%)" : "all-time_low_pct",
                "RSI" : "rsi",
                "Earnings" : "earnings",
                "IPO Date" : "ipo_date",
                "Optionable" : "optionable",
                "Shortable" : "shortable",
                "Employees" : "employees",
                "Change from Open (%)" : "change_from_open_pct",
                "Gap (%)" : "gap_pct",
                "Recom" : "recom",
                "Avg Volume (m USD)" : "avg_volume_m_usd",
                "Rel Volume" : "rel_volume",
                "Volume" : "volume",
                "Target Price" : "target_price",
                "Prev Close" : "prev_close",
                "Open" : "open",
                "High" : "high",
                "Low" : "low",
                "Price" : "price",
                "Change (%)" : "change_pct"
            }
        },
        'table_description': {
            'name': 'Finviz_Stocks_Description'
        }
    },
    'ManufacturingPmi': {
        'report_table': {
            'name': 'US_Man_Pmi_Report',
            'map': {
                'year': 'year',
                'month': 'month',
                'headline': 'headline',
                'highlights': 'highlights',
                'overview': 'overview',
                'comments': 'comments',
                'commodities_up': 'commodities_up',
                'commodities_down': 'commodities_down',
                'commodities_short': 'commodities_short',
                'index_summary': 'index_summary',
                'new_orders': 'new_orders',
                'production': 'production',
                'employment': 'employment',
                'supplier_deliveries': 'supplier_deliveries',
                'inventories': 'inventories',
                'customer_inventories': 'customer_inventories',
                'prices': 'prices',
                'backlog_orders': 'backlog_orders',
                'export_orders': 'export_orders',
                'imports': 'imports',
                'buying_policy': 'buying_policy',
                'pmi_index_value': 'pmi_index_value',
                'pmi_direction': 'pmi_direction',
                'pmi_change_rate': 'pmi_change_rate',
                'pmi_trend_months': 'pmi_trend_months',
                'new_orders_index_value': 'new_orders_index_value',
                'new_orders_direction': 'new_orders_direction',
                'new_orders_change_rate': 'new_orders_change_rate',
                'new_orders_trend_months': 'new_orders_trend_months',
                'production_index_value': 'production_index_value',
                'production_direction': 'production_direction',
                'production_change_rate': 'production_change_rate',
                'production_trend_months': 'production_trend_months',
                'employment_index_value': 'employment_index_value',
                'employment_direction': 'employment_direction',
                'employment_change_rate': 'employment_change_rate',
                'employment_trend_months': 'employment_trend_months',
                'supplier_deliveries_index_value': 'supplier_deliveries_index_value',
                'supplier_deliveries_direction': 'supplier_deliveries_direction',
                'supplier_deliveries_change_rate': 'supplier_deliveries_change_rate',
                'supplier_deliveries_trend_months': 'supplier_deliveries_trend_months',
                'inventories_index_value': 'inventories_index_value',
                'inventories_direction': 'inventories_direction',
                'inventories_change_rate': 'inventories_change_rate',
                'inventories_trend_months': 'inventories_trend_months',
                'customer_inventories_index_value': 'customer_inventories_index_value',
                'customer_inventories_direction': 'customer_inventories_direction',
                'customer_inventories_change_rate': 'customer_inventories_change_rate',
                'customer_inventories_trend_months': 'customer_inventories_trend_months',
                'prices_index_value': 'prices_index_value',
                'prices_direction': 'prices_direction',
                'prices_change_rate': 'prices_change_rate',
                'prices_trend_months': 'prices_trend_months',
                'backlog_orders_index_value': 'backlog_orders_index_value',
                'backlog_orders_direction': 'backlog_orders_direction',
                'backlog_orders_change_rate': 'backlog_orders_change_rate',
                'backlog_orders_trend_months': 'backlog_orders_trend_months',
                'export_orders_index_value': 'export_orders_index_value',
                'export_orders_direction': 'export_orders_direction',
                'export_orders_change_rate': 'export_orders_change_rate',
                'export_orders_trend_months': 'export_orders_trend_months',
                'imports_index_value': 'imports_index_value',
                'imports_direction': 'imports_direction',
                'imports_change_rate': 'imports_change_rate',
                'imports_trend_months': 'imports_trend_months',
                'overall_economy_direction': 'overall_economy_direction',
                'overall_economy_change_rate': 'overall_economy_change_rate',
                'overall_economy_trend_months': 'overall_economy_trend_months',
                'manufacturing_sector_direction': 'manufacturing_sector_direction',
                'manufacturing_sector_change_rate': 'manufacturing_sector_change_rate',
                'manufacturing_sector_trend_months': 'manufacturing_sector_trend_months',
                'new_orders_higher_pct': 'new_orders_higher_pct',
                'new_orders_same_pct': 'new_orders_same_pct',
                'new_orders_lower_pct': 'new_orders_lower_pct',
                'production_higher_pct': 'production_higher_pct',
                'production_same_pct': 'production_same_pct',
                'production_lower_pct': 'production_lower_pct',
                'employment_higher_pct': 'employment_higher_pct',
                'employment_same_pct': 'employment_same_pct',
                'employment_lower_pct': 'employment_lower_pct',
                'supplier_deliveries_slower_pct': 'supplier_deliveries_slower_pct',
                'supplier_deliveries_same_pct': 'supplier_deliveries_same_pct',
                'supplier_deliveries_faster_pct': 'supplier_deliveries_faster_pct',
                'inventories_higher_pct': 'inventories_higher_pct',
                'inventories_same_pct': 'inventories_same_pct',
                'inventories_lower_pct': 'inventories_lower_pct',
                'customer_inventories_reporting_pct': 'customer_inventories_reporting_pct',
                'customer_inventories_too_high_pct': 'customer_inventories_too_high_pct',
                'customer_inventories_about_right_pct': 'customer_inventories_about_right_pct',
                'customer_inventories_too_low_pct': 'customer_inventories_too_low_pct',
                'prices_higher_pct': 'prices_higher_pct',
                'prices_same_pct': 'prices_same_pct',
                'prices_lower_pct': 'prices_lower_pct',
                'backlog_orders_reporting_pct': 'backlog_orders_reporting_pct',
                'backlog_orders_higher_pct': 'backlog_orders_higher_pct',
                'backlog_orders_same_pct': 'backlog_orders_same_pct',
                'backlog_orders_lower_pct': 'backlog_orders_lower_pct',
                'export_orders_reporting_pct': 'export_orders_reporting_pct',
                'export_orders_higher_pct': 'export_orders_higher_pct',
                'export_orders_same_pct': 'export_orders_same_pct',
                'export_orders_lower_pct': 'export_orders_lower_pct',
                'imports_reporting_pct': 'imports_reporting_pct',
                'imports_higher_pct': 'imports_higher_pct',
                'imports_same_pct': 'imports_same_pct',
                'imports_lower_pct': 'imports_lower_pct',
                'capex_lead_time_avg': 'capex_lead_time_avg',
                'capex_lead_time_hand_to_mouth_pct': 'capex_lead_time_hand_to_mouth_pct',
                'capex_lead_time_thirty_days_pct': 'capex_lead_time_thirty_days_pct',
                'capex_lead_time_sixty_days_pct': 'capex_lead_time_sixty_days_pct',
                'capex_lead_time_ninety_days_pct': 'capex_lead_time_ninety_days_pct',
                'capex_lead_time_six_months_pct': 'capex_lead_time_six_months_pct',
                'capex_lead_time_year_plus_pct': 'capex_lead_time_year_plus_pct',
                'production_lead_time_avg': 'production_lead_time_avg',
                'production_lead_time_hand_to_mouth_pct': 'production_lead_time_hand_to_mouth_pct',
                'production_lead_time_thirty_days_pct': 'production_lead_time_thirty_days_pct',
                'production_lead_time_sixty_days_pct': 'production_lead_time_sixty_days_pct',
                'production_lead_time_ninety_days_pct': 'production_lead_time_ninety_days_pct',
                'production_lead_time_six_months_pct': 'production_lead_time_six_months_pct',
                'production_lead_time_year_plus_pct': 'production_lead_time_year_plus_pct',
                'mro_lead_time_avg': 'mro_lead_time_avg',
                'mro_lead_time_hand_to_mouth_pct': 'mro_lead_time_hand_to_mouth_pct',
                'mro_lead_time_thirty_days_pct': 'mro_lead_time_thirty_days_pct',
                'mro_lead_time_sixty_days_pct': 'mro_lead_time_sixty_days_pct',
                'mro_lead_time_ninety_days_pct': 'mro_lead_time_ninety_days_pct',
                'mro_lead_time_six_months_pct': 'mro_lead_time_six_months_pct',
                'mro_lead_time_year_plus_pct': 'mro_lead_time_year_plus_pct'
            }
        },
        'rankings_table': {
            'name': 'US_Man_Industry_Ranking',
            'map': {
                'Year': 'year',
                'Month': 'month',
                'Apparel, Leather & Allied Products': 'apparel_PMI',
                'Chemical Products': 'chemical_PMI',
                'Computer & Electronic Products': 'computer_electronics_PMI',
                'Electrical Equipment, Appliances & Components': 'electrical_equipment_PMI',
                'Fabricated Metal Products': 'fabricated_metal_PMI',
                'Food, Beverage & Tobacco Products': 'food_beverage_tobacco_PMI',
                'Furniture & Related Products': 'furniture_PMI',
                'Machinery': 'machinery_PMI',
                'Miscellaneous Manufacturing': 'miscellaneous_PMI',
                'Nonmetallic Mineral Products': 'non_metallic_mineral_PMI',
                'Paper Products': 'paper_PMI',
                'Petroleum & Coal Products': 'petroleum_coal_PMI',
                'Plastics & Rubber Products': 'plastic_rubber_PMI',
                'Primary Metals': 'metals_PMI',
                'Printing & Related Support Activities': 'printing_PMI',
                'Textile Mills': 'textiles_PMI',
                'Transportation Equipment': 'transportation_PMI',
                'Wood Products': 'wood_PMI',
                'Apparel, Leather & Allied Products - New Orders': 'apparel_NewOrders',
                'Chemical Products - New Orders': 'chemical_NewOrders',
                'Computer & Electronic Products - New Orders': 'computer_electronics_NewOrders',
                'Electrical Equipment, Appliances & Components - New Orders': 'electrical_equipment_NewOrders',
                'Fabricated Metal Products - New Orders': 'fabricated_metal_NewOrders',
                'Food, Beverage & Tobacco Products - New Orders': 'food_beverage_tobacco_NewOrders',
                'Furniture & Related Products - New Orders': 'furniture_NewOrders',
                'Machinery - New Orders': 'machinery_NewOrders',
                'Miscellaneous Manufacturing - New Orders': 'miscellaneous_NewOrders',
                'Nonmetallic Mineral Products - New Orders': 'non_metallic_mineral_NewOrders',
                'Paper Products - New Orders': 'paper_NewOrders',
                'Petroleum & Coal Products - New Orders': 'petroleum_coal_NewOrders',
                'Plastics & Rubber Products - New Orders': 'plastic_rubber_NewOrders',
                'Primary Metals - New Orders': 'metals_NewOrders',
                'Printing & Related Support Activities - New Orders': 'printing_NewOrders',
                'Textile Mills - New Orders': 'textiles_NewOrders',
                'Transportation Equipment - New Orders': 'transportation_NewOrders',
                'Wood Products - New Orders': 'wood_NewOrders'
            }
        }
    },
    'ServicesPmi': {
        'report_table': {
            'name': 'US_Ser_Pmi_Report',
            'map': {
                'year': 'year',
                'month': 'month',
                'headline': 'headline',
                'highlights': 'highlights',
                'overview': 'overview',
                'comments': 'comments',
                'commodities_up': 'commodities_up',
                'commodities_down': 'commodities_down',
                'commodities_short': 'commodities_short',
                'index_summary': 'index_summary',
                'new_orders': 'new_orders',
                'employment': 'employment',
                'supplier_deliveries': 'supplier_deliveries',
                'inventories': 'inventories',
                'prices': 'prices',
                'backlog_orders': 'backlog_orders',
                'export_orders': 'export_orders',
                'imports': 'imports',
                'business_activity': 'business_activity',
                'inventory_sentiment': 'inventory_sentiment',
                'pmi_index_value': 'pmi_index_value',
                'pmi_direction': 'pmi_direction',
                'pmi_change_rate': 'pmi_change_rate',
                'pmi_trend_months': 'pmi_trend_months',
                'new_orders_index_value': 'new_orders_index_value',
                'new_orders_direction': 'new_orders_direction',
                'new_orders_change_rate': 'new_orders_change_rate',
                'new_orders_trend_months': 'new_orders_trend_months',
                'business_activity_index_value': 'business_activity_index_value',
                'business_activity_direction': 'business_activity_direction',
                'business_activity_change_rate': 'business_activity_change_rate',
                'business_activity_trend_months': 'business_activity_trend_months',
                'employment_index_value': 'employment_index_value',
                'employment_direction': 'employment_direction',
                'employment_change_rate': 'employment_change_rate',
                'employment_trend_months': 'employment_trend_months',
                'supplier_deliveries_index_value': 'supplier_deliveries_index_value',
                'supplier_deliveries_direction': 'supplier_deliveries_direction',
                'supplier_deliveries_change_rate': 'supplier_deliveries_change_rate',
                'supplier_deliveries_trend_months': 'supplier_deliveries_trend_months',
                'inventories_index_value': 'inventories_index_value',
                'inventories_direction': 'inventories_direction',
                'inventories_change_rate': 'inventories_change_rate',
                'inventories_trend_months': 'inventories_trend_months',
                'prices_index_value': 'prices_index_value',
                'prices_direction': 'prices_direction',
                'prices_change_rate': 'prices_change_rate',
                'prices_trend_months': 'prices_trend_months',
                'backlog_orders_index_value': 'backlog_orders_index_value',
                'backlog_orders_direction': 'backlog_orders_direction',
                'backlog_orders_change_rate': 'backlog_orders_change_rate',
                'backlog_orders_trend_months': 'backlog_orders_trend_months',
                'export_orders_index_value': 'export_orders_index_value',
                'export_orders_direction': 'export_orders_direction',
                'export_orders_change_rate': 'export_orders_change_rate',
                'export_orders_trend_months': 'export_orders_trend_months',
                'imports_index_value': 'imports_index_value',
                'imports_direction': 'imports_direction',
                'imports_change_rate': 'imports_change_rate',
                'imports_trend_months': 'imports_trend_months',
                'inventory_sentiment_index_value': 'inventory_sentiment_index_value',
                'inventory_sentiment_direction': 'inventory_sentiment_direction',
                'inventory_sentiment_change_rate': 'inventory_sentiment_change_rate',
                'inventory_sentiment_trend_months': 'inventory_sentiment_trend_months',
                'overall_economy_direction': 'overall_economy_direction',
                'overall_economy_change_rate': 'overall_economy_change_rate',
                'overall_economy_trend_months': 'overall_economy_trend_months',
                'services_sector_direction': 'services_sector_direction',
                'services_sector_change_rate': 'services_sector_change_rate',
                'services_sector_trend_months': 'services_sector_trend_months',
                'new_orders_higher_pct': 'new_orders_higher_pct',
                'new_orders_same_pct': 'new_orders_same_pct',
                'new_orders_lower_pct': 'new_orders_lower_pct',
                'business_activity_higher_pct': 'business_activity_higher_pct',
                'business_activity_same_pct': 'business_activity_same_pct',
                'business_activity_lower_pct': 'business_activity_lower_pct',
                'employment_higher_pct': 'employment_higher_pct',
                'employment_same_pct': 'employment_same_pct',
                'employment_lower_pct': 'employment_lower_pct',
                'supplier_deliveries_slower_pct': 'supplier_deliveries_slower_pct',
                'supplier_deliveries_same_pct': 'supplier_deliveries_same_pct',
                'supplier_deliveries_faster_pct': 'supplier_deliveries_faster_pct',
                'inventories_higher_pct': 'inventories_higher_pct',
                'inventories_same_pct': 'inventories_same_pct',
                'inventories_lower_pct': 'inventories_lower_pct',
                'prices_higher_pct': 'prices_higher_pct',
                'prices_same_pct': 'prices_same_pct',
                'prices_lower_pct': 'prices_lower_pct',
                'backlog_orders_higher_pct': 'backlog_orders_higher_pct',
                'backlog_orders_same_pct': 'backlog_orders_same_pct',
                'backlog_orders_lower_pct': 'backlog_orders_lower_pct',
                'export_orders_higher_pct': 'export_orders_higher_pct',
                'export_orders_same_pct': 'export_orders_same_pct',
                'export_orders_lower_pct': 'export_orders_lower_pct',
                'imports_higher_pct': 'imports_higher_pct',
                'imports_same_pct': 'imports_same_pct',
                'imports_lower_pct': 'imports_lower_pct',
                'inventory_sentiment_too_high_pct': 'inventory_sentiment_too_high_pct',
                'inventory_sentiment_about_right_pct': 'inventory_sentiment_about_right_pct',
                'inventory_sentiment_too_low_pct': 'inventory_sentiment_too_low_pct'
            }
        },
        'rankings_table': {
            'name': 'US_Ser_Industry_Ranking',
            'map': {
                'Year': 'year',
                'Month': 'month',
                'Accommodation & Food Services': 'accommodation_food_PMI',
                'Agriculture, Forestry, Fishing & Hunting': 'agriculture_forestry_PMI',
                'Arts, Entertainment & Recreation': 'arts_entertainment_PMI',
                'Construction': 'construction_PMI',
                'Educational Services': 'education_PMI',
                'Finance & Insurance': 'finance_insurance_PMI',
                'Health Care & Social Assistance': 'healthcare_PMI',
                'Information': 'information_PMI',
                'Management of Companies & Support Services': 'company_management_PMI',
                'Mining': 'mining_PMI',
                'Other Services': 'other_PMI',
                'Professional, Scientific & Technical Services': 'technical_services_PMI',
                'Public Administration': 'public_admin_PMI',
                'Real Estate, Rental & Leasing': 'real_estate_PMI',
                'Retail Trade': 'retail_trade_PMI',
                'Transportation & Warehousing': 'transportation_warehousing_PMI',
                'Utilities': 'utilities_PMI',
                'Wholesale Trade': 'wholesale_trade_PMI',
                'Accommodation & Food Services - Business Activity': 'accommodation_food_BusinessActivity',
                'Agriculture, Forestry, Fishing & Hunting - Business Activity': 'agriculture_forestry_BusinessActivity',
                'Arts, Entertainment & Recreation - Business Activity': 'arts_entertainment_BusinessActivity',
                'Construction - Business Activity': 'construction_BusinessActivity',
                'Educational Services - Business Activity': 'education_BusinessActivity',
                'Finance & Insurance - Business Activity': 'finance_insurance_BusinessActivity',
                'Health Care & Social Assistance - Business Activity': 'healthcare_BusinessActivity',
                'Information - Business Activity': 'information_BusinessActivity',
                'Management of Companies & Support Services - Business Activity': 'company_management_BusinessActivity',
                'Mining - Business Activity': 'mining_BusinessActivity',
                'Other Services - Business Activity': 'other_BusinessActivity',
                'Professional, Scientific & Technical Services - Business Activity': 'technical_services_BusinessActivity',
                'Public Administration - Business Activity': 'public_admin_BusinessActivity',
                'Real Estate, Rental & Leasing - Business Activity': 'real_estate_BusinessActivity',
                'Retail Trade - Business Activity': 'retail_trade_BusinessActivity',
                'Transportation & Warehousing - Business Activity': 'transportation_warehousing_BusinessActivity',
                'Utilities - Business Activity': 'utilities_BusinessActivity',
                'Wholesale Trade - Business Activity': 'wholesale_trade_BusinessActivity'
            }
        }
    }      
}

MAN_REPORT = {
#    The dictionary keys are the names of different sections in the ISM reports.
#    Each key has a dictionary as value, containing information on how to locate the relevant section in the HTML structure.
#    This dictionary has three keys: tag, attrs, and methods.
#    The tag key contains the HTML tag to search for using BeautifulSoup's .find() method (e.g., 'h1', 'h2', 'p').
#    The attrs key contains the key-word arguments for .find() in the form of key-value pairs, e.g., {'class_': 'text-center'}.
#    The methods key contains a list of dictionaries, each providing a sequential chain of methods to apply after the initial .find() method, to locate the target HTML content.
#    Each dictionary in the methods list contains the method name to call, the tag to search for, and key-word arguments.

#    Take the below key: value pair as an example:
#        'comm_price_up': {
#            'tag': 'h3',
#            'attrs': {'id': 'commodities'},
#            'methods': [
#                {'name': 'find_next_sibling', 'tag': 'div', 'attrs': {}},
#                {'name': 'findChild', 'tag': 'p', 'attrs': {}}
#            ]
#        }

#    This tells us that we need to find the <h3> tag with id='commodities' and then, find the next sibling with <div> tag, and then find the first child with <p> tag.
#    target_html_tag = soup.find('h3', id='commodities').find_next_sibling('div').findChild('p')

#    These dictionaries are used in the find_content function.

    'headline': {
        'tag': 'h1',
        'attrs': {},
        'methods': []
    },
    'title': {
        'tag': 'h1',
        'attrs': {},
        'methods': [
            {'name': 'find_next_sibling', 'tag': 'h1', 'attrs': {}}
        ]
    },
    'highlights': {
        'tag': 'h3',
        'attrs': {'class_': 'text-center'},
        'methods': []
    },
    'overview': {
        'tag': 'h3',
        'attrs': {'class_': 'text-center'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'comments': {
        'tag': 'h3',
        'attrs': {'id': 'respondentsSay'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'ul', 'attrs': {}}
        ]
    },
    'full_pmi_table': {
        'tag': 'h3',
        'attrs': {'id': 'respondentsSay'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'comm_price_up': {
        'tag': 'h3',
        'attrs': {'id': 'commodities'},
        'methods': [
            {'name': 'find_next_sibling', 'tag': 'div', 'attrs': {}},
            {'name': 'findChild', 'tag': 'p', 'attrs': {}}
        ]
    },
    'comm_price_down': {
        'tag': 'h3',
        'attrs': {'id': 'commodities'},
        'methods': [
            {'name': 'find_next_sibling', 'tag': 'div', 'attrs': {}},
            {'name': 'find_next_sibling', 'tag': 'div', 'attrs': {}},
            {'name': 'findChild', 'tag': 'p', 'attrs': {}}
        ]
    },
    'comm_supply_short': {
        'tag': 'h3',
        'attrs': {'id': 'commodities'},
        'methods': [
            {'name': 'find_next_sibling', 'tag': 'p', 'attrs': {}}
        ]
    },
    'index_summary': {
        'tag': 'h3',
        'attrs': {'id': 'manIndexSumm'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'new_orders_text': {
        'tag': 'h3',
        'attrs': {'string': 'New Orders'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'new_orders_table': {
        'tag': 'h3',
        'attrs': {'string': 'New Orders'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'production_text': {
        'tag': 'h3',
        'attrs': {'id': 'production'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'production_table': {
        'tag': 'h3',
        'attrs': {'id': 'production'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'employment_text': {
        'tag': 'h3',
        'attrs': {'id': 'employment'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'employment_table': {
        'tag': 'h3',
        'attrs': {'id': 'employment'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'supplier_deliveries_text': {
        'tag': 'h3',
        'attrs': {'id': 'supplierDeliveries'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'supplier_deliveries_table': {
        'tag': 'h3',
        'attrs': {'id': 'supplierDeliveries'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'inventories_text': {
        'tag': 'h3',
        'attrs': {'id': 'inventories'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'inventories_table': {
        'tag': 'h3',
        'attrs': {'id': 'inventories'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'customer_inventories_text': {
        'tag': 'h3',
        'attrs': {'id': 'customersInventories'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'customer_inventories_table': {
        'tag': 'h3',
        'attrs': {'id': 'customersInventories'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'prices_text': {
        'tag': 'h3',
        'attrs': {'id': 'prices'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'prices_table': {
        'tag': 'h3',
        'attrs': {'id': 'prices'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'backlog_orders_text': {
        'tag': 'h3',
        'attrs': {'id': 'backlogOrders'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'backlog_orders_table': {
        'tag': 'h3',
        'attrs': {'id': 'backlogOrders'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'export_orders_text': {
        'tag': 'h3',
        'attrs': {'id': 'newExportOrders'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'export_orders_table': {
        'tag': 'h3',
        'attrs': {'id': 'newExportOrders'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'imports_text': {
        'tag': 'h3',
        'attrs': {'id': 'imports'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'imports_table': {
        'tag': 'h3',
        'attrs': {'id': 'imports'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'buying_policy_text': {
        'tag': 'h3',
        'attrs': {'id': 'buyingPolicy'},
        'methods': [
            {'name': 'find_parent', 'tag': 'div', 'attrs': {}},
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'buying_policy_table': {
        'tag': 'h3',
        'attrs': {'id': 'buyingPolicy'},
        'methods': [
            {'name': 'find_parent', 'tag': 'div', 'attrs': {}},
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    }
}

SERV_REPORT = {
    'headline': {
        'tag': 'h1',
        'attrs': {},
        'methods': []
    },
    'title': {
        'tag': 'h1',
        'attrs': {},
        'methods': [
            {'name': 'find_next_sibling', 'tag': 'h1', 'attrs': {}}
        ]
    },
    'highlights': {
        'tag': 'h3',
        'attrs': {'class_': 'text-center'},
        'methods': []
    },
    'overview': {
        'tag': 'h3',
        'attrs': {'class_': 'text-center'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {'class_': None}}
        ]
    },
    'comments': {
        'tag': 'h3',
        'attrs': {'id': 'respondentsSay'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'ul', 'attrs': {}}
        ]
    },
    'full_pmi_table': {
        'tag': 'h3',
        'attrs': {'id': 'respondentsSay'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'comm_price_up': {
        'tag': 'h3',
        'attrs': {'id': 'commodities'},
        'methods': [
            {'name': 'find_next_sibling', 'tag': 'div', 'attrs': {}},
            {'name': 'findChild', 'tag': 'p', 'attrs': {}}
        ]
    },
    'comm_price_down': {
        'tag': 'h3',
        'attrs': {'id': 'commodities'},
        'methods': [
            {'name': 'find_next_sibling', 'tag': 'div', 'attrs': {}},
            {'name': 'find_next_sibling', 'tag': 'div', 'attrs': {}},
            {'name': 'findChild', 'tag': 'p', 'attrs': {}}
        ]
    },
    'comm_supply_short': {
        'tag': 'h3',
        'attrs': {'id': 'commodities'},
        'methods': [
            {'name': 'find_next_sibling', 'tag': 'p', 'attrs': {}}
        ]
    },
    'index_summary': {
        'tag': 'h3',
        'attrs': {'string': lambda text: 'SERVICES INDEX SUMMARIES' in text if text else False},
        'methods': [
            {'name': 'find_parent', 'tag': 'div', 'attrs': {}},
            {'name': 'find_next_sibling', 'tag': 'div', 'attrs': {}},
            {'name': 'findChildren', 'tag': 'p', 'attrs': {}}
        ]
    },
    'business_activity_text': {
        'tag': 'h3',
        'attrs': {'id': 'businessActivity'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'business_activity_table': {
        'tag': 'h3',
        'attrs': {'id': 'businessActivity'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'new_orders_text': {
        'tag': 'h3',
        'attrs': {'string': 'New Orders'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'new_orders_table': {
        'tag': 'h3',
        'attrs': {'string': 'New Orders'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'employment_text': {
        'tag': 'h3',
        'attrs': {'string': 'Employment'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'employment_table': {
        'tag': 'h3',
        'attrs': {'string': 'Employment'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'supplier_deliveries_text': {
        'tag': 'h3',
        'attrs': {'string': 'Supplier Deliveries'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'supplier_deliveries_table': {
        'tag': 'h3',
        'attrs': {'string': 'Supplier Deliveries'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'inventories_text': {
        'tag': 'h3',
        'attrs': {'string': 'Inventories'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'inventories_table': {
        'tag': 'h3',
        'attrs': {'string': 'Inventories'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'prices_text': {
        'tag': 'h3',
        'attrs': {'string': 'Prices'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'prices_table': {
        'tag': 'h3',
        'attrs': {'string': 'Prices'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'backlog_orders_text': {
        'tag': 'h3',
        'attrs': {'string': 'Backlog of Orders'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'backlog_orders_table': {
        'tag': 'h3',
        'attrs': {'string': 'Backlog of Orders'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'export_orders_text': {
        'tag': 'h3',
        'attrs': {'string': 'New Export Orders'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'export_orders_table': {
        'tag': 'h3',
        'attrs': {'string': 'New Export Orders'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'inventory_sentiment_text': {
        'tag': 'h3',
        'attrs': {'id': 'inventorySentiment'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'inventory_sentiment_table': {
        'tag': 'h3',
        'attrs': {'id': 'inventorySentiment'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'imports_text': {
        'tag': 'h3',
        'attrs': {'string': 'Imports'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'imports_table': {
        'tag': 'h3',
        'attrs': {'string': 'Imports'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    }
}