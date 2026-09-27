import polars as pl
import pytest
import tidypolars4sci as tp


def test_ungrouped_row_number():
    df = tp.tibble(x=[None, 'a', 'a'])
    result = df.mutate(tp.row_number(), doubled=tp.row_number() * 2).to_polars()
    assert result['row_number'].to_list() == [1, 2, 3]
    assert result['doubled'].to_list() == [2, 4, 6]
    assert result.columns == ['x', 'row_number', 'doubled']


@pytest.mark.parametrize('explicit_grouping', [False, True])
@pytest.mark.parametrize('keys, expected', [
    ('group', [1, 2, 1, 3, 3, 1]),
    (['group', 'subgroup'], [1, 2, 1, 3, 3, 4]),
])
def test_group_ids(explicit_grouping, keys, expected):
    df = tp.tibble(
        position=list(range(6)), group=['b', 'a', 'b', None, None, 'b'],
        subgroup=[0, 0, 0, 0, 0, 1],
    )
    kwargs = dict(group_id=tp.row_number(), offset=tp.row_number() + 10,
                  copied=tp.col('group_id'), size=pl.len())
    result = (df.group_by(keys).mutate(**kwargs) if explicit_grouping
              else df.mutate(by=keys, **kwargs)).arrange('position').to_polars()
    assert result['group_id'].to_list() == expected
    assert result['copied'].to_list() == expected
    assert result['offset'].to_list() == [i + 10 for i in expected]
    assert result['size'].to_list() == [expected.count(i) for i in expected]
    assert result.columns == df.names + list(kwargs)


@pytest.mark.parametrize('grouping', ['none', 'by', 'group_by'])
def test_empty_row_number(grouping):
    df = tp.tibble({'group': pl.Series([], dtype=pl.String)})
    result = (df.group_by('group').mutate(id=tp.row_number())
              if grouping == 'group_by' else
              df.mutate(id=tp.row_number(), by='group' if grouping == 'by' else None))
    result = result.to_polars()
    assert result.shape == (0, 2)
    assert result.schema['id'] == pl.Int64
