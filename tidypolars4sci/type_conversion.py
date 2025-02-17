import polars as pl
from .utils import (
    _col_expr,
)

__all__ = [
    # Type conversion
    "as_boolean", "as_character", "as_categorical", "as_factor",
    "as_float", "as_integer", "as_logical", "as_string", "cast"
    ]


def as_boolean(x):
    """
    Convert column to string. Alias to as_logical (R naming).
    """
    return as_logical(x)

def as_categorical(*args, **kwargs):
    "Convert to factor. Alias for as_factor"
    return as_factor(*args, **kwargs)

def as_character(x):
    """
    Convert to string. Defaults to Utf8.

    Parameters
    ----------
    x : Str 
        Column to operate on

    Examples
    --------
    >>> df.mutate(string_x = tp.as_string('x'))
    # or equivalently
    >>> df.mutate(character_x = tp.as_character('x'))
    """
    x = _col_expr(x)
    return x.cast(pl.Utf8)

def as_factor(x, levels = None):
    """
    Convert to factor (R naming), equlivalent to Enum or
    Categorical (polars), depending on whether 'levels' is provided. 

    Parameters
    ----------
    x : Str
        Column to operate on

    levels : list of str
        Categories to use in the factor. The catogories will be ordered
        as they appear in the list. If None (default), it will
        create an unordered factor (polars Categorical).

    Examples
    --------
    >>> df.mutate(factor_x = tp.as_factor('x'))
    # or equivalently
    >>> df.mutate(categorical_x = tp.as_categorical('x'))
    """
    x = _col_expr(x)
    x = x.cast(pl.String)
    if levels is None:
        x = x.cast(pl.Categorical)
    else:
        x = x.cast(pl.Enum(levels))
    return x

def as_float(x):
    """
    Convert to float. Defaults to Float64.

    Parameters
    ----------
    x : Expr, Series
        Column to operate on

    Examples
    --------
    >>> df.mutate(float_x = tp.as_float(col('x')))
    """
    x = _col_expr(x)
    return x.cast(pl.Float64)

def as_integer(x):
    """
    Convert to integer. Defaults to Int64.

    Parameters
    ----------
    x : Expr
        Column to operate on

    Examples
    --------
    >>> df.mutate(int_x = tp.as_integer(col('x')))
    """
    x = _col_expr(x)
    return x.cast(pl.Int64)

def as_logical(x):
    """
    Convert to a boolean (polars) or 'logical' (R naming)

    Parameters
    ----------
    x : Str
        Column to operate on

    Examples
    --------
    >>> df.mutate(bool_x = tp.as_boolean(col('x')))
    # or equivalently
    >>> df.mutate(logical_x = tp.as_logical(col('x')))
    """
    x = _col_expr(x)
    return x.cast(pl.Boolean)

def as_string(x):
    '''
    Convert column to string. Alias to as_character (R naming).
    Equivalent to Utf8 type (polars)
    '''
    return as_character(x)

def cast(x, dtype):
    """
    General type conversion.

    Parameters
    ----------
    x : Expr, Series
        Column to operate on
    dtype : DataType
        Type to convert to

    Examples
    --------
    >>> df.mutate(abs_x = tp.cast(col('x'), tp.Float64))
    """
    x = _col_expr(x)
    return x.cast(dtype)
