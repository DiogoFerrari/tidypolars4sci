import tidypolars4sci as tp


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
