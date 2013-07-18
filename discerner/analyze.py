"""
discerner.analyze
~~~~~~~~~~~~~~~~~
"""
from __future__ import print_function
from random import randint
from time import time

from memorandum.finder import get_yearly_data
from memorandum.exceptions import HTTPStatusCodeError
from memorandum.stats import find_highest_outliers
from memorandum.utils import convert_wiki_date_to_datetime
from requests.exceptions import ConnectionError

from discerner import cruncher
from discerner.constants import RANDOM_VIEWS_PER_STOCK
from discerner.defaults import logger
from discerner.exceptions import SkipEvaluationError

# XXX Globals feels pretty weird.
pre_rets = []
post_rets = []


def analyze_pages(func, args):
    """
    Base function for analyzing wiki pages
    """
    cruncher.load_r_funcs()
    pages = cruncher.get_pages(args)
    mapping = {
        "RANDOM": lambda *args: (None, None),
        "RECENT": analyze_page_view_data, 
        "HISTORICAL": analyze_page_view_data
    }

    for key, page in pages.iteritems():
        logger.info("Analyzing for symbol: {}, page: {}".format(key, page))
        outliers, quantile = mapping[args.data_type](args, key, page)
        func(args, key, outliers, quantile)

    perform_analysis(args)
    perform_final_action(args)


def analyze_page_view_data(args, key, page):
    """
    For RECENT and HISTORICAL viewing get wikipedia page views stats and 
    analyze them
    """
    try:
        data = get_yearly_data(page)
    except (ConnectionError, HTTPStatusCodeError) as error:
        logger.warn(error.message)
       
    outliers, quantile = find_highest_outliers(
        data, prob=[args.probability]
    )
    return outliers, quantile


def for_historical_views(args, key, outliers, quantile):
    """
    Analyze all desired wikipedia pages over the current year for trends
    involving outliers in page views and accompanying changes in stock
    prices 10 business days afterwards.
    """
    prices = cruncher.get_stock_data(args, key)
    for date, val in outliers:
        day_of_year = int(
            convert_wiki_date_to_datetime(date).strftime("%j")) - 1
        get_pre_and_post_returns(args, day_of_year, prices)


def for_random_views(args, key, *other_args):
    """
    Analyze data for a completely random set of views
    """
    prices = cruncher.get_stock_data(args, key)
    for _ in xrange(RANDOM_VIEWS_PER_STOCK):
        day = randint(args.interval, len(prices) - args.interval)
        get_pre_and_post_returns(args, day, prices)


def for_recent_views(args, key, outliers, quantile):
    """
    Analyze all desired wikipedia for recent outliers. Respond to user if the
    company has generated an outlier within the past number of user specified
    days
    """
    for date, val in outliers:
        unix_time = int(convert_wiki_date_to_datetime(
            date, hour=23).strftime("%s")
        )
        cur_unix_time = time()
        if cur_unix_time - unix_time <= 60 * 60 * 12 * args.days:
            print(key, date, val, quantile)


def get_pre_and_post_returns(args, day, prices):
    """
    Append pre and post return data
    """
    try:
        pre_start = cruncher.get_end_index(
            prices, day, index=-1 * args.interval
        )
        pre_end = cruncher.get_end_index(
            prices, pre_start, index=args.interval - 1
        )
        post_start = cruncher.get_start_index(prices, day, index=1)
        post_end = cruncher.get_end_index(
            prices, post_start, index=args.interval - 1
        )
    except SkipEvaluationError:
        logger.debug(
            "The day {} does not support being evaluated".format(day)
        )
    else:
        logger.debug("Appending to returns")
        pre_rets.append(
            (prices[pre_end] - prices[pre_start]) / prices[pre_start]
        )
        post_rets.append(
            (prices[post_end] - prices[post_start]) / prices[post_start]
        )


def perform_analysis(args):
    """
    Perform analysis on returned data
    """
    if args.data_type in ("HISTORICAL", "RANDOM"):
        inflection_data = cruncher.find_number_inflection_points(
            pre_rets, post_rets
        )
        print(
            "Number of inflection points: {}, "
            "Percentage Inflection points: {}".format(
                inflection_data[0], inflection_data[1]
            )
        )


def perform_final_action(args):
    """
    Depending on whether we are looking for historical or recent views, perform
    the last action
    """
    mapping = {
        "HISTORICAL": cruncher.make_plot,
        "RANDOM": cruncher.make_plot,
        "RECENT": lambda *args: logger.info("Finished")
    }
    mapping[args.data_type](pre_rets, post_rets)
