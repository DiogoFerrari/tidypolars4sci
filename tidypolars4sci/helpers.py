import polars as pl
import copy
from .utils import (
    _as_list,
    _col_expr,
    _col_exprs,
    _is_constant,
    _is_list,
    _is_iterable,
    _is_series,
    _is_string,
    _str_to_lit
    )

__all__ = ["contains", "ends_with", "everything", "starts_with",
           'matches', "desc", "across", "lag", "DescCol"]

def contains(match, ignore_case = True):
    """
    Contains a literal string

    Parameters
    ----------
    match : str
        String to match columns

    ignore_case : bool
        If TRUE, the default, ignores case when matching names.

    Examples
    --------
    >>> df = tp.tibble({'a': range(3), 'b': range(3), 'c': ['a', 'a', 'b']})
    >>> df.select(contains('c'))
    """
    if ignore_case == True:
        out = f"^*(?i){match}.*$"
    else:
        out = f"^*{match}.*$"
    return out

def ends_with(match, ignore_case = True):
    """
    Ends with a suffix

    Parameters
    ----------
    match : str
        String to match columns

    ignore_case : bool
        If TRUE, the default, ignores case when matching names.

    Examples
    --------
    >>> df = tp.tibble({'a': range(3), 'b_code': range(3), 'c_code': ['a', 'a', 'b']})
    >>> df.select(ends_with('code'))
    """
    if ignore_case == True:
        out = f"^.*(?i){match}$"
    else:
        out = f"^.*{match}$"
    return out

def everything():
    """
    Selects all columns

    Examples
    --------
    >>> df = tp.tibble({'a': range(3), 'b': range(3), 'c': ['a', 'a', 'b']})
    >>> df.select(everything())
    """
    return "*"

def starts_with(match, ignore_case = True):
    """
    Starts with a prefix

    Parameters
    ----------
    match : str
        String to match columns
    ignore_case : bool
        If TRUE, the default, ignores case when matching names.

    Examples
    --------
    >>> df = tp.tibble({'a': range(3), 'add': range(3), 'sub': ['a', 'a', 'b']})
    >>> df.select(starts_with('a'))
    """
    if ignore_case == True:
        out = f"^(?i){match}.*$"
    else:
        out = f"^{match}.*$"
    return out

def matches(match, ignore_case = False):
    """
    Matches pattern

    Parameters
    ----------
    match : str
        String to match columns
    ignore_case : bool
        If True, the default, ignores case when matching names.

    Examples
    --------
    >>> df = tp.tibble({'a': range(3), 'add': range(3), 'sub': ['a', 'a', 'b']})
    >>> df.select(tp.maches('a'))
    """
    if ignore_case == True:
        out = f"^(?i){match}.*$"
    else:
        out = f"^{match}.*$"
    return out

def desc(x):
    """Mark a column to order in descending"""
    x = copy.copy(x)
    x = _col_expr(x)
    x.__class__ = DescCol
    return x

class DescCol(pl.Expr):
    pass

def across(cols, fn = lambda x: x, names_prefix = None):
    """
    Apply a function across a selection of columns

    Parameters
    ----------
    cols : list
        Columns to operate on
    fn : lambda
        A function or lambda to apply to each column
    names_prefix : Optional - str
        Prefix to append to changed columns

    Examples
    --------
    >>> df = tp.tibble(x = ['a', 'a', 'b'], y = range(3), z = range(3))
    >>> df.mutate(across(['y', 'z'], lambda x: x * 2))
    >>> df.mutate(across(tp.Int64, lambda x: x * 2, names_prefix = "double_"))
    >>> df.summarize(across(['y', 'z'], tp.mean), by = 'x')
    """
    _cols = _col_exprs(_as_list(cols))
    exprs = [fn(_col) for _col in _cols]
    if names_prefix != None:
        exprs = [expr.name.prefix(names_prefix) for expr in exprs]
    return exprs

def lag(x, n: int = 1, default = None):
    """
    Get lagging values

    Parameters
    ----------
    x : Expr, Series
        Column to operate on

    n : int
        Number of positions to lag by

    default : optional
        Value to fill in missing values

    Examples
    --------
    >>> df.mutate(lag_x = tp.lag(col('x')))
    >>> df.mutate(lag_x = tp.lag('x'))
    """
    x = _col_expr(x)
    return x.shift(n, fill_value = default)
