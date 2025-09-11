from dataclasses import dataclass

@dataclass(frozen=True)
class config:
    path = './Leading Indicators and Stocks.db'
    exe_limit = 32766