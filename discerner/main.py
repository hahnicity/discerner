"""
discerner.main
~~~~~~~~~~~~~~
"""
#!/usr/bin/env python
from argparse import ArgumentParser

from discerner.analyze import (
    analyze_pages, for_historical_views, for_recent_views, for_random_views
)
from discerner.constants import DAYS
from discerner.defaults import analysis_interval
from discerner.pages import get_financial_pages, get_sp500


def parse_argv():
    """
    Parse argv for which pages we wish to analyze
    """
    parser = ArgumentParser()
    parser.add_argument(
        "-d", 
        "--days", 
        type=int,
        default=DAYS,
        help="Number of days back we wish to look for data"
    )
    parser.add_argument(
        "-p", 
        "--probability", 
        type=float,
        default=.9,
        help="The percentile of page views to view for eg: .88"
    )
    parser.add_argument(
        "-t",
        "--data-type",
        choices=["RANDOM", "RECENT", "HISTORICAL"],
        required=True,
        help="The type of data we wish to parse for",
    )
    parser.add_argument(
        "-i", 
        "--interval", 
        type=int,
        default=analysis_interval,
        help="Interval to analyze data over (days)"
    )
    add_subparsers(parser)
    return parser.parse_args()


def add_subparsers(parser):
    """
    Add subparsers for financial pages, sp500 stocks and custom stocks
    """
    subparsers = parser.add_subparsers(help="Which pages to analyze")
    add_financials_subparser(subparsers)
    add_sp500_subparser(subparsers)
    add_custom_subparser(subparsers)


def add_sp500_subparser(subparsers):
    """
    Add subparser for S&P 500 Stocks
    """
    sp500 = subparsers.add_parser("sp500", help="Analyze the S&P 500")
    sp500.set_defaults(pages=get_sp500)


def add_custom_subparser(subparsers):
    """
    Add subparser for customized stock picks
    """
    custom = subparsers.add_parser(
        "custom", help="Analyze set of user defined pages"
    )
    custom.add_argument(
        "pages", 
        nargs="*", 
        help="Symbol:Wikipage to analyze, eg: AAPL:Apple_Inc MSFT:Microsoft"
    )


def add_financials_subparser(subparsers):
    """
    Add subparser for financial pages
    """
    financials = subparsers.add_parser(
        "financials", help="Analyze financial info pages"
    )
    financials.set_defaults(pages=get_financial_pages)
    

def main():
    """
    Discerner console script
    """
    args = parse_argv()
    mapping = {
        "RANDOM": for_random_views,
        "RECENT": for_recent_views, 
        "HISTORICAL": for_historical_views
    }
    for_view_type = mapping[args.data_type]
    analyze_pages(for_view_type, args)


if __name__ == "__main__":
    main()
