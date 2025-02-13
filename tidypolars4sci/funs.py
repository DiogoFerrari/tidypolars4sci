import polars as pl
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

__all__ = ["case_when", "n_distinct", 'map']

def between(x, left, right):
    """
    Test if values of a column are between two values

    Parameters
    ----------
    x : Expr, Series
        Column to operate on
    left : int
        Value to test if column is greater than or equal to
    right : int
        Value to test if column is less than or equal to

    Examples
    --------
    >>> df = tp.tibble(x = range(4))
    >>> df.filter(tp.between(col('x'), 1, 3))
    """
    x = _col_expr(x)
    return x.is_between(left, right)

def coalesce(*args):
    """
    Coalesce missing values

    Parameters
    ----------
    args : Expr
        Columns to coalesce

    Examples
    --------
    >>> df.mutate(abs_x = tp.cast(col('x'), tp.Float64))
    """
    args = _as_list(args)
    expr = if_else(args[0].is_null(), args[1], args[0])
    if len(args) > 2:
        locs = range(2, len(args))
        for i in locs:
            expr = if_else(expr.is_null(), args[i], expr)
    return expr

def if_else(condition, true, false):
    """
    If Else

    Parameters
    ----------
    condition : Expr
        A logical expression
    true :
        Value if the condition is true
    false :
        Value if the condition is false

    Examples
    --------
    >>> df = tp.tibble(x = range(1, 4))
    >>> df.mutate(if_x = tp.if_else(col('x') < 2, 1, 2))
    """
    return pl.when(condition).then(true).otherwise(false)

def lead(x, n: int = 1, default = None):
    """
    Get leading values

    Parameters
    ----------
    x : Expr, Series
        Column to operate on

    n : int
        Number of positions to lead by

    default : optional
        Value to fill in missing values

    Examples
    --------
    >>> df.mutate(lead_x = tp.lead(col('x')))
    >>> df.mutate(lead_x = col('x').lead())
    """
    x = _col_expr(x)
    return x.shift(-n, fill_value = default)

def n_distinct(x):
    """
    Get number of distinct values in a column

    Parameters
    ----------
    x : Expr, Series
        Column to operate on

    Examples
    --------
    >>> df.summarize(min_x = tp.n_distinct('x'))
    >>> df.summarize(min_x = tp.n_distinct(col('x')))
    """
    x = _col_expr(x)
    return x.n_unique()

def rep(x, times = 1):
    """
    Replicate the values in x

    Parameters
    ----------
    x : const, Series
        Value or Series to repeat
    times : int
        Number of times to repeat

    Examples
    --------
    >>> tp.rep(1, 3)
    >>> tp.rep(pl.Series(range(3)), 3)
    """
    if _is_constant(x):
        out = [x]
    elif _is_series(x):
        out = x.to_list()
    elif _is_list(x):
        out = x
    elif isinstance(x, tibble):
        out = pl.concat([x for i in range(times)]).pipe(from_polars)
    elif _is_iterable(x):
        out = list(x)
    else:
        ValueError("Incompatible type")
    if _is_list(out):
        out = pl.Series(out * times)
    return out

def replace_null(x, replace = None):
    """
    Replace null values

    Parameters
    ----------
    x : Expr, Series
        Column to operate on

    Examples
    --------
    >>> df = tp.tibble(x = [0, None], y = [None, None])
    >>> df.mutate(x = tp.replace_null(col('x'), 1))
    """
    if replace == None: return x
    return x.fill_null(replace)

def round(x, decimals = 0):
    """
    Get column standard deviation

    Parameters
    ----------
    x : Expr, Series
        Column to operate on
    decimals : int
        Decimals to round to

    Examples
    --------
    >>> df.mutate(x = tp.round(col('x')))
    """
    x = _col_expr(x)
    return x.round(decimals)

def row_number():
    """
    Return row number

    Examples
    --------
    >>> df.mutate(row_num = tp.row_number())
    """
    return pl.int_range(0, pl.len()) + 1

def case_when(*args, _default = None):
    """
    Case when

    Parameters
    ----------
    expr : Expr
        A logical expression

    Examples
    --------
    >>> df = tp.tibble(x = range(1, 4))
    >>> df.mutate(
    >>>    case_x = tp.case_when(tp.col('x') < 2, 1,
    >>>                          tp.col('x') < 3, 2,
    >>>                          _default = 0)
    >>> )
    """
    conditions = [args[i] for i in range(0, len(args), 2)]
    values = [args[i] for i in range(1, len(args), 2)]
    values = [_str_to_lit(value) for value in values]
    for i in range(len(conditions)):
        if i == 0:
            expr = pl.when(conditions[i]).then(values[i])
        else:
            expr = expr.when(conditions[i]).then(values[i])
    _default = _str_to_lit(_default)
    expr = expr.otherwise(_default)
    return expr

def map(cols, _fun):
    """
    Apply function by row

    Parameters
    ----------
    cols : list of str
       A list with the name of the columns in the data to apply function

    _ fun : a function
       The function to apply to the columns. The function is applied
       to each row separately
    

    """
    # map_groups give a list of lists. I flatten it so that _fun can refer to the list of
    # columns (cols) simply bu index
    flatten = lambda cols: [item for series in cols for item in list(series)]
    res = pl.map_groups(cols, lambda cols: _fun(flatten(cols))).over(pl.int_range(pl.len()))
    return res
