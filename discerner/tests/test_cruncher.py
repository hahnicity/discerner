"""
discerner.tests.test_cruncher
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from argparse import Namespace
from nose.tools import eq_, raises
from rpy2.rinterface import NARealType

from discerner.cruncher import (
    find_non_nan, get_start_index, get_end_index, get_pages
)
from discerner.exceptions import SkipEvaluationError
from discerner.pages import get_financial_pages


def test_find_non_nan():
    """
    Test discerner.analyze.find_non_nan for the case of non reversed values
    """
    data = [1, 2, 3, NARealType(), 5, 6]
    index = find_non_nan(data, 3)
    eq_(data[index], 5)


def test_find_non_nan_reversed():
    """
    Test discerner.analyze.find_non_nan for case of reversed data
    """
    data = [1, 2, 3, NARealType(), 5, 6]
    index = find_non_nan(data, 3, reverse=True)
    eq_(data[index], 3)


@raises(SkipEvaluationError)
def test_find_non_nan_error_raised():
    """
    Test discerner.analyze.find_non_nan for case where an error is raised
    """
    data = [1, 2, 3, NARealType()]
    find_non_nan(data, 3)


def test_get_start_index():
    """
    Test discerner.get_start_index for success cases
    """
    data = [0, 1, 2, 3, 4, 5]
    start = get_start_index(data, 3)
    eq_(data[start], 4)

    data = [0, 1, 2, NARealType(), 4]
    start = get_start_index(data, 2)
    eq_(data[start], 4)
    

@raises(SkipEvaluationError)
def test_get_start_index_error_raised1():
    """
    Test discerner.get_start_index for case where an error is raised 
    by find_non_nan function
    """
    data = [0, 1, 2, NARealType()]
    get_start_index(data, 2)


@raises(SkipEvaluationError)
def test_get_start_index_error_raised2():
    """
    Test discerner.get_start_index for case where an error is raised
    by get_start_index function
    """
    data = [0, 1, 2, NARealType()]
    get_start_index(data, 3)


def test_get_start_index_with_negative_indexing():
    """
    Test discerner.cruncher.get_start_index with negative indexing
    """
    data = range(15)
    start = get_start_index(data, 14, index=-13)
    eq_(start, 1)


def test_get_end_index():
    """
    Test discerner.get_end_index for success cases
    """
    data = range(15)
    end = get_end_index(data, 0)
    eq_(data[end], 13)


def test_get_end_index_with_nan():
    """
    Test discerner.get_end_index for success case with nan value
    """
    data = range(13)
    data.append(NARealType())
    data.extend([14, 15])
    end = get_end_index(data, 0)
    eq_(data[end], 12)


def test_get_end_index_for_close_to_end_of_range():
    """
    Test discerner.get_end_index for cases where index is close to end of data
    """
    data = range(8)
    end = get_end_index(data, 0)
    eq_(data[end], 7)

    data = range(8)
    data.append(NARealType())
    end = get_end_index(data, 0)
    eq_(data[end], 7)


def test_get_end_index_for_negative_indexing():
    """
    Test discerner.cruncher.get_end_index for negative indexing
    """
    data = range(15)
    end = get_end_index(data, 14, index=-1)
    eq_(end, 13)


@raises(SkipEvaluationError)
def test_get_end_index_for_error():
    """
    Test discerner.get_end_index for error case
    """
    data = [1, NARealType()]
    get_end_index(data, 0)


def test_get_pages_for_function():
    """
    Test discerner.analyze.get_pages with a function
    """
    args = Namespace(pages=get_financial_pages)
    pages = get_pages(args)
    eq_(pages, get_financial_pages())


def test_get_pages_for_list():
    """
    Test discerner.analyze.get_pages with a list
    """
    args = Namespace(pages=["MSFT:Microsoft", "AAPL:Apple_Inc"])
    pages = get_pages(args)
    expected = {"MSFT": "Microsoft", "AAPL": "Apple_Inc"}
    for symbol in pages:
        eq_(expected[symbol], pages[symbol])
