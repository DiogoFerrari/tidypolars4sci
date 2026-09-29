import tidypolars4sci as tp


def test_descriptive_statistics_per_variable_missing():
    """Grouped statistics use each variable's own non-missing values."""
    df = tp.tibble({
        'x': [1, 2, None, 4],
        'g': ['a', None, 'a', 'b'],
        'unused': [None, None, None, None],
    })

    actual = df.descriptive_statistics('x', groups='g', include_categorical=False)

    assert actual.nrow == 2
    assert actual.pull('g').to_list() == ['a', 'b']
    assert actual.pull('N').to_list() == [1, 1]
    assert actual.pull('Missing (%)').to_list() == [50.0, 0.0]


def test_descriptive_statistics_only_categorical_vars():
    """Works when none of the requested variables is numeric."""
    df = tp.tibble({
        'a': ['x', 'y', 'z'],
        'b': [1, 2, 3],
        'g': ['u', 'u', 'v'],
    })

    actual = df.descriptive_statistics('a')
    assert actual.nrow == 3
    assert actual.pull('Variable').to_list() == ['a (x)', 'a (y)', 'a (z)']

    grouped = df.descriptive_statistics('a', groups='g')
    assert grouped.nrow == 3
    assert 'g' in grouped.names

    empty = df.descriptive_statistics('a', include_categorical=False)
    assert empty.nrow == 0


def test_descriptive_statistics_disjoint_missingness():
    """Variables missing on different rows are each summarised on their own rows."""
    df = tp.tibble({
        'y': [1.0, 2.0, None, None],
        'p': [None, None, 0, 1],
    })

    actual = df.descriptive_statistics(['y', 'p']).arrange('Variable')

    assert actual.pull('N').to_list() == [2, 2]
    assert actual.pull('Missing (%)').to_list() == [50.0, 50.0]
    assert actual.pull('Mean').to_list() == [0.5, 1.5]
