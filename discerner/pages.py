"""
discerner.pages
~~~~~~~~~~~~~~~
"""
import re

from bs4 import BeautifulSoup
import requests

from discerner.constants import SP500_TABLE_CLASS, SP500_URL


def get_financial_pages():
    """
    Get all relevant financial pages
    """
    # XXX temporary proof of concept. Well maybe not ...
    return {
        "Arrangements between railroads": "Arrangements_between_railroads",
        "Asset": "Assets",
        "Black-Scholes": "Black_Scholes",
        "Bond": "Bond_(finance)",
        "Brokerage": "Brokerage_firm",
        "Bubble": "Stock_market_bubble",
        "Bucket shop": "Bucket_shop_(stock_market)",
        "Business Cycle": "Business_cycle",
        "Buying in": "Buying_in_(securities)",
        "Call option": "Call_option",
        "Capital Market": "Capital_market",
        "Car loan": "Car_finance",
        "Cash": "Cash",
        "Concentrated stock": "Concentrated_stock",
        "Coupon": "Coupon_(bond)",
        "Derivative": "Derivative_(finance)",
        "Dividend": "Dividend",
        "Dow Industrials": "Dow_Industrials",
        "Economics": "Economics",
        "Equity investment": "Equity_investment",
        "Finance": "Finance",
        "Financial Advisor": "Financial_adviser",
        "Financial Crisis": "Economic_crises",
        "Financial Planner": "Financial_planner",
        "Financial Institution": "Financial_institution",
        "Futures": "Futures_contract",
        "GICS": "Global_Industry_Classification_Standard",
        "Golden share": "Golden_share",
        "House stock": "House_stock",
        "Insider Trading": "Insider_trading",
        "Interest Rate": "Interest_rate",
        "Investment": "Investment",
        "Investment Banking": "Investment_banking",
        "Join Stock Company": "Joint_stock_company",
        "Long": "Long_(finance)",
        "Money Managers": 
        "Category:Money_managers",
        "Mutual Funds": "Mutual_Funds",
        "Mortgage loan": "Mortgage_loan",
        "NASDAQ": "NASDAQ",
        "Options": "Stock_option",
        "Personal Finance": "Personal_finance",
        "Penny Stocks": "Penny_stock",
        "Portfolio Manager": "Portfolio_manager",
        "Put option": "Put_option",
        "Real Estate": "Real_estate",
        "Refinancing": "Refinancing",
        "S&P 500": "S%26P500",
        "Scripophily": "Scricophily",
        "Security": "Security_(finance)",
        "Share": "Share_(finance)",
        "Short": "Short_(finance)",
        "Speculation": "Speculation",
        "Stock": "Stock",
        "Stock broker": "Stockbroker",
        "Stock Dilution": "Stock_dilution",
        "Stock Market": "Stock_market",
        "Strike Price": "Strike_price",
        "Student loan": "Student_loan",
        "Swap": "Swap_(finance)",
    }


def get_sp500():
    """
    Get ticker symbol and wiki url suffix for all companies on S&P 500 index
    """
    def parse_company():
        generator_index = 1
        for child in company.children:
            generator_index += 1
            if child.string:
                symbol = child.string
            try:
                href = child.find_next_sibling().a.get("href")
            except AttributeError:
                continue
            else:
                href = href if re.search("/wiki", href) else ""
            if generator_index > 2:
                break
        return symbol, href

    sp500 = {}
    html = requests.get(SP500_URL).text
    soup = BeautifulSoup(html)
    companies = soup.find("table", {"class": SP500_TABLE_CLASS}).find_all("tr")
    for company in companies:
        symbol, href = parse_company()
        sp500[symbol] = href.split("/")[-1]

    partial = {company: page for company, page in sp500.iteritems() if page}
    if "Company" in partial:
        del partial["Company"]

    return partial
