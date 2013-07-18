"""
discerner.exceptions
~~~~~~~~~~~~~~~~~~~~
"""


class SkipEvaluationError(Exception):
    def __init__(self, message=None):
        default = "The given date and set of price data do not support a "\
                  "valid evaluation"
        message = message or default
        super(SkipEvaluationError, self).__init__(message)
