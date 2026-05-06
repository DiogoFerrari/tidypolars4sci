import tidypolars4sci as tp


def test_descriptive_statistics_drops_nulls_in_used_vars():
    """Can compute grouped descriptive statistics after complete-case filtering."""
    df = tp.tibble({
        'x': [1, 2, None, 4],
        'g': ['a', None, 'a', 'b'],
        'unused': [None, None, None, None],
    })

    actual = df.descriptive_statistics('x', groups='g', include_categorical=False)

    assert actual.nrow == 2
    assert actual.pull('g').to_list() == ['a', 'b']
    assert actual.pull('N').to_list() == [1, 1]
    assert actual.pull('Missing (%)').to_list() == [0.0, 0.0]
