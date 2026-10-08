import pytest
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


def test_descriptive_statistics_default_stats_unchanged():
    """Default output keeps every statistic in the historical order."""
    df = tp.tibble(score=[1, 2, None], w=[1.5, 2.5, 3.5], g=['a', 'a', 'b'])

    actual = df.descriptive_statistics(['score', 'w'], groups='g', include_type=True)
    assert actual.names == ['g', 'Variable', 'N', 'Missing (%)', 'Mean',
                            'Std.Dev.', 'Min', '25%', '50%', '75%', 'Max', 'Type']


def test_descriptive_statistics_stats_subset():
    """Only the requested statistics are returned, in the order given."""
    df = tp.tibble(score=[1, 2, None], w=[1.5, 2.5, 3.5], g=['a', 'a', 'b'])

    actual = df.descriptive_statistics(['score', 'w'], stats=['Max', 'N'])
    assert actual.names == ['Variable', 'Max', 'N']

    single = df.descriptive_statistics('score', stats='Mean')
    assert single.names == ['Variable', 'Mean']
    assert single.pull('Mean').to_list() == [1.5]

    grouped = df.descriptive_statistics(['score', 'w'], groups={'g': 'G'},
                                        stats=['N'], include_type=True)
    assert grouped.names == ['G', 'Variable', 'N', 'Type']

    full = df.descriptive_statistics(['score', 'w'])
    subset = df.descriptive_statistics(['score', 'w'], stats=['Std.Dev.'])
    assert full.pull('Std.Dev.').to_list() == subset.pull('Std.Dev.').to_list()


def test_descriptive_statistics_stats_not_applicable_are_omitted():
    """Statistics absent for categorical-only output are dropped silently."""
    df = tp.tibble(a=['x', 'y', 'z'], b=[1, 2, 3])

    actual = df.descriptive_statistics('a', stats=['Min', 'N'])
    assert actual.names == ['Variable', 'N']

    empty = df.descriptive_statistics('a', include_categorical=False, stats=['N'])
    assert empty.nrow == 0


def test_descriptive_statistics_unknown_stat_rejected():
    df = tp.tibble(b=[1, 2, 3])
    with pytest.raises(AssertionError, match="Unknown statistic"):
        df.descriptive_statistics('b', stats=['Median'])
