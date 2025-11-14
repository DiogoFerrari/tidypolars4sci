import inspect
import polars as pl
import polars.selectors as cs
from operator import not_
from itertools import chain
from pathlib import Path
from typing import Union
from urllib.parse import urlparse
from urllib.request import url2pathname


__all__ = []

def _list_flatten(l):
    l = [x if isinstance(x, list) else [x] for x in l]
    return list(chain.from_iterable(l))

def _as_list(x):
    if type(x).__name__ == 'DataTypeClass':
        out = [x]
    elif _safe_len(x) == 0:
        out = []
    elif _is_series(x):
        out = x.to_list()
    elif _is_tuple(x):
        # Helpful to convert args to a list
        out = [val.to_list() if _is_series(val) else val for val in x]
        out = _list_flatten(x)
    elif _is_list(x):
        out = _list_flatten(x)
    else:
        out = [x]
    return out

# Convert kwargs to col() expressions with alias
def _kwargs_as_exprs(kwargs):
    return [_lit_expr(expr).alias(key) for key, expr in kwargs.items()]

def _safe_len(x):
    if x == None:
        return 0
    else:
        return len(x)

def _uses_by(by):
    if _is_expr(by) | _is_string(by):
        return True
    elif isinstance(by, list):
        # Allow passing an empty list to `by`
        if _safe_len(by) == 0:
            return False
        else:
            return True
    else:
        return False

def _is_boolean(x):
    return isinstance(x, bool)

def _is_constant(x):
    return _is_boolean(x) | _is_float(x) | _is_integer(x) | _is_string(x)

def _is_expr(x):
    return isinstance(x, pl.Expr)

def _is_float(x):
    return isinstance(x, float)

def _is_integer(x):
    return isinstance(x, int)

def _is_iterable(x):
    return hasattr(x, '__iter__') & not_(_is_string(x))

def _is_list(x):
    return isinstance(x, list)

def _is_series(x):
    return isinstance(x, pl.Series)

def _is_string(x):
    return isinstance(x, str)

def _is_tuple(x):
    return isinstance(x, tuple)

def _is_type(x):
    return type(x).__name__ == 'DataTypeClass'

def _lit_expr(x):
    if not_(_is_expr(x)):
        x = pl.lit(x)
    return x

#  Wrap all str inputs in col()  
def _col_exprs(x):
    if _is_list(x) | _is_series(x):
        return [_col_expr(val) for val in x]
    else:
        return [_col_expr(x)]

def _col_expr(x):
    if _is_expr(x) | _is_series(x) | cs.is_selector(x):
        return x
    elif _is_string(x) | _is_type(x):
        return pl.col(x)
    else:
       raise ValueError("Invalid input for column selection") 

def _repeat(x, times):
    if not_(_is_list(x)):
        x = [x]
    return x * times

def _mutate_cols(df, exprs):
    for expr in exprs:
        df = df.with_columns(expr)
    return df

def _str_to_lit(x):
    if _is_string(x):
        x = pl.lit(x)
    return x

def _filter_kwargs_for(func, kwargs):
    sig = inspect.signature(func)
    allowed = sig.parameters.keys()
    return {k: v for k, v in kwargs.items() if k in allowed}

def _expand_to_full_path(p: Union[str, Path]) -> str:
    # """
    # Convert a relative path, '~' path, or Path object
    # into a fully expanded absolute string path.
    # """
    # Ensure it is a Path object
    p = Path(p)

    # Expand home (~) and get absolute path
    return str(p.expanduser().resolve())

def _expand_to_full_path_or_url(p: Union[str, Path]) -> str:
    # """
    # Convert a filesystem path (relative, '~', or Path) into a fully expanded
    # absolute string path.

    # If `p` is a URL (e.g. 'https://...'), it is returned unchanged.
    # If `p` is a file URL (e.g. 'file:///home/user/file.txt'),
    # it is converted to a local absolute path.
    # """
    if not p:
        return p
        

    # If it's already a Path, we know it's a filesystem path, not a URL
    if isinstance(p, Path):
        return str(p.expanduser().resolve())

    # Otherwise, it's a string: might be URL or path
    s = str(p)

    # Quick check: treat strings containing '://' as potential URLs
    if "://" in s:
        parsed = urlparse(s)

        # file:// URL -> convert to local path
        if parsed.scheme == "file":
            local_path = url2pathname(parsed.path)
            return str(Path(local_path).expanduser().resolve())

        # Other URL schemes (http, https, s3, etc.) -> return unchanged
        if parsed.scheme:
            return s

    # Otherwise, treat it as a normal filesystem path
    return str(Path(s).expanduser().resolve())
