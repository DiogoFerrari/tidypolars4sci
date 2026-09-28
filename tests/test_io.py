import math
import pytest
import polars as pl
import tidypolars4sci as tp
from tidypolars4sci.io import read_data

TEXT_EXTS = ['csv', 'tsv', 'txt', 'dat']

def _missing_data():
    return tp.tibble(x = [1.5, float('nan'), 2.0, None],
                     i = [1, None, 3, 4],
                     s = ['a b', 'b', None, 'd'])

def _round_trip(df, fn, **kws):
    df.save_data(str(fn), silently=True, **kws)
    out = tp.read_data(fn=str(fn), silently=True, **kws)
    return out[0] if isinstance(out, tuple) else out

def _assert_same_values(actual, expected):
    for a, e in zip(actual.to_polars().rows(), expected.to_polars().rows()):
        for va, ve in zip(a, e):
            if isinstance(ve, float) and math.isnan(ve):
                assert isinstance(va, float) and math.isnan(va)
            else:
                assert va == ve

@pytest.mark.parametrize("ext", TEXT_EXTS + ['parquet'])
def test_round_trip_keeps_types_and_missing(tmp_path, ext):
    """save_data then read_data keeps dtypes, NaN and null"""
    df = _missing_data()
    out = _round_trip(df, tmp_path / f"data.{ext}")
    assert out.to_polars().schema == df.to_polars().schema
    _assert_same_values(out, df)

@pytest.mark.parametrize("ext", TEXT_EXTS)
def test_round_trip_custom_sep(tmp_path, ext):
    """A custom separator works when given to both functions"""
    df = _missing_data()
    out = _round_trip(df, tmp_path / f"data.{ext}", sep='|')
    assert out.to_polars().schema == df.to_polars().schema

def test_round_trip_dta_has_no_index(tmp_path):
    """Stata files are saved without the pandas index"""
    df = _missing_data()
    out = _round_trip(df, tmp_path / "data.dta")
    assert out.names == df.names

def _leading_missing_data(n):
    return tp.tibble(x = [float('nan')] * (n - 3) + [1.5, None, 2.0],
                     i = [None] * (n - 2) + [7, 8],
                     s = [None] * (n - 1) + ['a'])

@pytest.mark.parametrize("large", [False, True])
def test_csv_leading_missing_values_read_as_numbers(tmp_path, monkeypatch, large):
    """Numeric columns with many leading missing values are not read as strings"""
    if large:
        # use the path for large files (types inferred from first rows only)
        monkeypatch.setattr(read_data, 'CSV_FULL_INFER_MAX_BYTES', 0)
    df = _leading_missing_data(read_data.CSV_INFER_ROWS + 500)
    out = _round_trip(df, tmp_path / "data.csv")
    assert out.to_polars().schema == df.to_polars().schema
    _assert_same_values(out, df)

@pytest.mark.parametrize("large", [False, True])
def test_csv_float_after_inferred_rows(tmp_path, monkeypatch, large):
    """A float after many integers makes the column Float64"""
    if large:
        monkeypatch.setattr(read_data, 'CSV_FULL_INFER_MAX_BYTES', 0)
    fn = tmp_path / "data.csv"
    fn.write_text('a;b\n' + '1;x\n' * (read_data.CSV_INFER_ROWS + 500) + '2.5;y\n')
    out = tp.read_data(fn=str(fn), silently=True)
    assert out.to_polars().schema == pl.Schema({'a': pl.Float64, 'b': pl.String})

def test_csv_user_infer_schema_length_is_respected(tmp_path):
    """A user-given infer_schema_length is passed as is to polars"""
    df = _leading_missing_data(200)
    df.save_data(str(tmp_path / "data.csv"), silently=True)
    out = tp.read_data(fn=str(tmp_path / "data.csv"), silently=True,
                       infer_schema_length=10)
    assert out.to_polars().schema['i'] == pl.String
