import tidypolars4sci as tp
import pandas as pd


def test_glimpse_accepts_regex_pattern(capsys):
    """Can print glimpse output for columns matched by regex."""
    df = tp.tibble({
        'x': [1, 2, 3],
        'long_name': ['alpha', 'beta', None],
    })

    df.glimpse('.')
    captured = capsys.readouterr()

    assert "Columns matching pattern '.'" in captured.out
    assert 'x' in captured.out
    assert 'long_name' in captured.out


def test_glimpse_arrow_strings_print_values_without_wrapper(capsys, monkeypatch):
    df = tp.tibble({'label': ['alpha', 'beta', None]})
    pandas_df = pd.DataFrame({
        'label': pd.Series(['alpha', 'beta', None], dtype='string[pyarrow]'),
    })
    monkeypatch.setattr(tp.tibble, 'to_pandas', lambda self: pandas_df)

    df.glimpse()
    output = capsys.readouterr().out

    assert 'ArrowStringArray' not in output
    assert "['alpha' 'beta' <NA>]" in output
    assert '[Rows: 3; Columns 1]' in output
