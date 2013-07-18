"""
discerner.cruncher
~~~~~~~~~~~~~~~~~~
"""
from datetime import datetime
from operator import add, sub
from os.path import dirname, join, realpath
import signal
import sys

from discerner.constants import NEW_YEARS_2013
from discerner.defaults import logger
from discerner.exceptions import SkipEvaluationError
from numpy import asarray
from rpy2 import robjects
from rpy2.robjects import numpy2ri
from rpy2.rinterface import NARealType

today = datetime.today().strftime("%Y-%m-%d")


def find_non_nan(data, index, reverse=False):
    """
    If a NaN has been identified at data[index] find the next position in our
    data where a NaN is not present
    """
    if reverse:
        data = data[:index + 1]
        data.reverse()
        op = sub
    else:
        data = data[index:]
        op = add

    for position, price in enumerate(data):
        if not isinstance(price, NARealType):
            return op(index, position)
    else:
        raise SkipEvaluationError()


def find_number_inflection_points(pre, post):
    """
    Given our return data find how many inflection points we have
    """
    inflections = 0
    rets = zip(pre, post)
    eval_ = lambda x: ((x[0] > 0 and x[1] < 0) or (x[0] < 0 and x[1] > 0))
    for i in rets:
        if eval_(i):
            inflections += 1

    return inflections, float(inflections) / len(rets)


def get_pages(args):
    """
    Return a dictionary of {symbol1: wikipage1, symbol2: ..., }
    """
    logger.debug("Getting all pages used")
    try:
        args.pages.__name__
    except AttributeError:
        logger.debug("Returning a custom set of pages")
        return {pair.split(":")[0]: pair.split(":")[1] for pair in args.pages}
    else:
        logger.debug("Returning pages for {}".format(args.pages.__name__))
        return args.pages()


def get_end_index(prices, start, index=13):
    """
    Get final date to look for in historical data
    """
    if start + index > len(prices) - 1:
        end = find_non_nan(prices, len(prices) - 1, reverse=True)
        if end <= start:
            raise SkipEvaluationError()
        return end
    
    if isinstance(prices[start + index], NARealType):
        return find_non_nan(prices, start + index, reverse=True)
    else:
        return start + index


def get_start_index(prices, day, index=1):
    """
    Get start date to look for in historical data
    """
    if day + index > len(prices) - 1:
        raise SkipEvaluationError()

    if isinstance(prices[day + index], NARealType):
        return find_non_nan(prices, day + index)
    else:
        return day + index


def get_stock_data(args, key):
    """
    Get data for a given stock
    """
    def stock_data(key):
        logger.info("Downloading price data for {}".format(key))
        # XXX DONT HARDCODE 2013
        return robjects.r["get.quotes"](
            key, NEW_YEARS_2013, today, "AdjClose", retclass="ts"
        )

    mapping = {"get_sp500": key, "get_financial_pages": "SPY"}
    
    try:
        key = mapping[args.pages.__name__]
    except (AttributeError, KeyError):
        prices = stock_data(key)
    else:
        prices = stock_data(key)

    return list(robjects.r["as.data.frame"](prices)[0])


def load_r_funcs():
    """
    Load necessary R functions
    """
    rfile_dir = realpath(dirname(__file__))
    rfile_path = join(rfile_dir, "stocks.r")
    robjects.r("""source('{}'); getClasses()""".format(rfile_path))


def make_plot(pre, post):
    """
    Plot the pre return values and post return values
    """
    data = make_returns_data(pre, post)
    numpy2ri.activate()
    column = robjects.r["c"]
    sequence = robjects.r["seq"]
    robjects.r["plot"](
        x=2, 
        y=2, 
        xlim=column(0, len(data["pre"]) - 1), 
        ylim=column(data["min"] - .1, data["max"] + .1),
        xlab="Event number", 
        ylab="Returns"
    )
    robjects.r["points"](
        x=sequence(0, len(data["pre"]) - 1), y=data["pre"], col="red", pch=19
    )
    robjects.r["points"](
        x=sequence(0, len(data["pre"]) - 1), y=data["post"], col="blue", pch=19
    )
    robjects.r["abline"](h=0)
    signal.signal(signal.SIGINT, lambda a, b: sys.exit(0))
    signal.pause()


def make_returns_data(pre, post):
    """
    Get all data we will need to make our graph
    """
    max_ = max([max(pre), max(post)])
    min_ = min([min(pre), min(post)])
    rets = sorted(
        zip(pre, post), 
        key=lambda x: 
        ((x[0] > 0 and x[1] < 0) or (x[0] < 0 and x[1] > 0)) and x[0] - x[1]
    )
    pre, post = zip(*rets)
    pre = asarray(pre)
    post = asarray(post)
    return {"pre": pre, "post": post, "max": max_, "min": min_}
