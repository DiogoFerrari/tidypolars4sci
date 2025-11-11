import polars as pl

__all__ = [
    'col', 'exclude', 'lit', 'Expr', 'Series', 'element',

    # dtypes
    'Int8', 'Int16', 'Int32', 'Int64',
    'UInt8', 'UInt16', 'UInt32', 'UInt64',
    'Float32', 'Float64', 'Boolean', 'Utf8',
    'List', 'Date', 'Datetime', 'Object',
    
    "is_character", "is_string", "is_factor", "is_ordered", "is_unordered",
    "is_integer", "is_float", "is_numeric",
]

col = pl.col
exclude = pl.exclude
lit = pl.lit
Expr = pl.Expr
Series = pl.Series
element = pl.element

# dtypes
Int8 = pl.Int8
Int16 = pl.Int16
Int32 = pl.Int32
Int64 = pl.Int64
UInt8 = pl.UInt8
UInt16 = pl.UInt16
UInt32 = pl.UInt32
UInt64 = pl.UInt64
Float32 = pl.Float32
Float64 = pl.Float64
Boolean = pl.Boolean
Utf8 = pl.Utf8
List = pl.List
Date = pl.Date
Datetime = pl.Datetime
Object = pl.Object

is_character = [pl.Utf8, pl.Enum, pl.Categorical]
is_string = pl.Utf8
is_factor = [pl.Enum, pl.Categorical]
is_ordered = pl.Enum
is_unordered = pl.Categorical
is_integer =  [pl.Int8, pl.Int16, pl.Int32, pl.Int64]
is_float = [pl.Float32, pl.Float64]
is_numeric = [pl.Int8, pl.Int16, pl.Int32, pl.Int64, pl.Float32, pl.Float64]
