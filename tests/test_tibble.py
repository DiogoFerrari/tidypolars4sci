import tidypolars4sci as tp
from tidypolars4sci import col
import inspect
import pandas as pd
import polars as pl
import pytest
from tidypolars4sci.utils import _repeat

def test_arrange1():
    """Can arrange ascending"""
    df = tp.tibble(x = ['a', 'a', 'b'], y = [2, 1, 3])
    actual = df.arrange('y')
    expected = tp.tibble(x = ['a', 'a', 'b'], y = [1, 2, 3])
    assert actual.equals(expected), "arrange ascending failed"
    assert type(actual) == tp.tibble, "arrange didn't return a tibble"

def test_arrange2():
    """Can arrange descending"""
    df = tp.tibble({'x': ['a', 'a', 'b'], 'y': [2, 1, 3]})
    actual = df.arrange(tp.desc('x'), 'y')
    expected = tp.tibble({'x': ['b', 'a', 'a'], 'y': [3, 1, 2]})
    assert actual.equals(expected), "arrange descending failed"

def test_arrange_across():
    """Can arrange across"""
    df = tp.tibble({'x': ['a', 'a', 'b'], 'y': [1, 2, 3], 'z': [1, 2, 3]})
    actual = df.arrange(
        tp.across(['x']),
        tp.across(['y', 'z'], tp.desc)
    )
    expected = tp.tibble(x = ['a', 'a', 'b'], y = [2, 1, 3], z = [2, 1, 3])
    assert actual.equals(expected), "arrange across failed"

def test_bind_cols_single():
    """Can bind_cols"""
    df1 = tp.tibble({'x': ['a', 'a', 'b'], 'y': [1, 2, 3]})
    df2 = tp.tibble({'z': [4, 4, 4]})
    actual = df1.bind_cols(df2)
    expected = tp.tibble({'x': ['a', 'a', 'b'], 'y': [1, 2, 3], 'z':[4, 4, 4]})
    assert actual.equals(expected), "bind_cols failed"
    assert type(actual) == tp.tibble, "bind_cols didn't return a tibble"

def test_bind_cols_multiple():
    """Can bind_cols multiple"""
    df1 = tp.tibble(x = range(3))
    df2 = tp.tibble(y = range(3))
    df3 = tp.tibble(z = range(3))
    actual = df1.bind_cols(df2, df3)
    expected = tp.tibble(x = range(3), y = range(3), z = range(3))
    assert actual.equals(expected), "multiple bind_cols failed"

def test_bind_rows_single():
    """Can bind rows"""
    df1 = tp.tibble({'x': ['a', 'a'], 'y': [2, 1]})
    df2 = tp.tibble({'x': ['b'], 'y': [3]})
    actual = df1.bind_rows(df2)
    expected = tp.tibble({'x': ['a', 'a', 'b'], 'y': [2, 1, 3]})
    assert actual.equals(expected), "bind_rows failed"
    assert type(actual) == tp.tibble, "bind_rows didn't return a tibble"

def test_bind_rows_auto_align():
    """Can bind rows"""
    df1 = tp.tibble(x = ['a', 'a'], y = [2, 1])
    df2 = tp.tibble(y = [3], x = ['b'])
    actual = df1.bind_rows(df2)
    expected = tp.tibble({'x': ['a', 'a', 'b'], 'y': [2, 1, 3]})
    assert actual.equals(expected), "bind_rows auto-align failed"

def test_bind_rows_multiple():
    """Can bind rows (multiple)"""
    df1 = tp.tibble({'x': ['a', 'a'], 'y': [2, 1]})
    df2 = tp.tibble({'x': ['b'], 'y': [3]})
    df3 = tp.tibble({'x': ['b'], 'y': [3]})
    actual = df1.bind_rows(df2, df3)
    expected = tp.tibble({'x': ['a', 'a', 'b', 'b'], 'y': [2, 1, 3, 3]})
    assert actual.equals(expected), "bind_rows multiple failed"

def test_clone():
    df = tp.tibble(x = range(3), y = range(3))
    actual = df.clone()
    assert type(actual) == tp.tibble, "clone didn't return a tibble"

def test_count_no_args():
    """Can count rows (no args)"""
    df = tp.tibble({'x': ['a', 'a', 'b'], 'y': [1, 1, 1]})
    actual = df.count()
    expected = tp.tibble({'n': [3]})
    assert actual.equals(expected), "count with no args failed"

def test_count_one_arg():
    """Can count rows (one arg)"""
    df = tp.tibble({'x': ['a', 'a', 'b'], 'y': [1, 1, 1]})
    actual = df.count('x', sort = True)
    expected = tp.tibble({'x': ['a', 'b'], 'n': [2, 1]})
    assert actual.equals(expected), "count with one arg failed"

def test_distinct_empty():
    """Can distinct columns"""
    df = tp.tibble({'x': ['a', 'a', 'b'], 'y': ['a', 'a', 'b']})
    actual = df.distinct().arrange('x', 'y')
    expected = tp.tibble({'x': ['a', 'b'], 'y': ['a', 'b']})
    assert actual.equals(expected), "empty distinct failed"
    assert type(actual) == tp.tibble, "distinct didn't return a tibble"

def test_distinct_select():
    """Can distinct columns"""
    df = tp.tibble({'x': ['a', 'a', 'b'], 'y': [2, 1, 3]})
    actual = df.distinct('x').arrange('x')
    expected = tp.tibble({'x': ['a', 'b']})
    assert actual.equals(expected), "distinct with select failed"

def test_drop():
    """Can drop columns"""
    df = tp.tibble(x = range(3), y = range(3))
    actual = df.drop('x')
    expected = tp.tibble(y = range(3))
    assert actual.equals(expected), "drop failed"
    assert type(actual) == tp.tibble, "drop didn't return a tibble"

def test_drop_null_empty():
    """Can drop nulls from all cols"""
    df = tp.tibble(x = [1, None, 3], y = [None, 2, 3], z = range(1, 4))
    actual = df.drop_null()
    expected = tp.tibble(x = [3], y = [3], z = [3])
    assert actual.equals(expected), "empty drop_null failed"
    assert type(actual) == tp.tibble, "drop_null didn't return a tibble"

def test_drop_null_select():
    """Can drop nulls with selection"""
    df = tp.tibble(x = [1, None, 3], y = [None, 2, 3], z = range(1, 4))
    actual = df.drop_null('x')
    expected = tp.tibble(x = [1, 3], y = [None, 3], z = [1, 3])
    assert actual.equals(expected, null_equal = True), "drop_null with selection failed"

def test_fill():
    """Can fill"""
    df = tp.tibble({'chr': ['a', None], 'int': [1, None]})
    actual = df.fill('chr', 'int')
    expected = tp.tibble({'chr': ['a', 'a'], 'int': [1, 1]})
    assert actual.equals(expected), "fill failed"
    assert type(actual) == tp.tibble, "fill didn't return a tibble"

def test_filter():
    """Can filter multiple conditions"""
    df = tp.tibble({'x': range(10), 'y': range(10)})
    actual = df.filter(col('x') <= 3, col('y') < 2)
    expected = tp.tibble({'x': range(2), 'y': range(2)})
    assert actual.equals(expected), "filter failed"
    assert type(actual) == tp.tibble, "filter didn't return a tibble"

def test_filter_grouped():
    df = tp.tibble(x = range(3), y = ['a', 'a', 'b'])
    actual = df.filter(col('x') <= col('x').mean(), by = 'y').arrange('y')
    expected = tp.tibble(x = [0, 2], y = ['a', 'b'])
    assert actual.equals(expected), "grouped filter failed"
    assert type(actual) == tp.tibble, "grouped filter didn't return a tibble"

def test_full_join():
    """Can perform a full join"""
    df1 = tp.tibble(x = ['a', 'a', 'b'], y = range(3))
    df2 = tp.tibble(x = ['a'], z = range(1))
    actual = df1.full_join(df2)
    expected = tp.tibble(x = ['a', 'a', 'b'], y = [0, 1, 2], z = [0, 0, None])
    assert actual.equals(expected, null_equal = True), "full_join failed"
    assert type(actual) == tp.tibble, "full_join didn't return a tibble"

def test_inner_join():
    """Can perform a inner join"""
    df1 = tp.tibble(x = ['a', 'a', 'b'], y = range(3))
    df2 = tp.tibble(x = ['a'], z = range(1))
    actual = df1.inner_join(df2)
    expected = tp.tibble(x = ['a', 'a'], y = [0, 1], z = [0, 0])
    assert actual.equals(expected), "inner_join failed"
    assert type(actual) == tp.tibble, "inner_join didn't return a tibble"

def test_left_join():
    """Can perform a left join"""
    df1 = tp.tibble(x = ['a', 'a', 'b'], y = range(3))
    df2 = tp.tibble(x = ['a', 'b'], z = range(2))
    actual = df1.left_join(df2)
    expected = tp.tibble(x = ['a', 'a', 'b'], y = range(3), z = [0, 0 ,1])
    assert actual.equals(expected), "left_join failed"
    assert type(actual) == tp.tibble, "left_join didn't return a tibble"

def test_mutate():
    """Can edit existing columns and can add columns"""
    df = tp.tibble({'x': _repeat(1, 3), 'y': _repeat(2, 3)})
    actual = df.mutate(double_x = col('x') * 2,
                       y = col('y') + 10,
                       y_plus_3 = col('y') + 3)
    expected = tp.tibble(
        x = _repeat(1, 3),
        y = _repeat(12, 3),
        double_x = _repeat(2, 3),
        y_plus_3 = _repeat(15, 3)
    )
    assert actual.equals(expected), "mutate failed"
    assert type(actual) == tp.tibble, "mutate didn't return a tibble"

def test_mutate_across():
    """Can mutate multiple columns simultaneously"""
    df = tp.tibble({'x': _repeat(1, 3), 'y': _repeat(2, 3)})
    actual = df.mutate(tp.across(tp.Int64, lambda x: x * 2),
                       x_plus_y = col('x') + col('y'))
    expected = tp.tibble(
        {'x': _repeat(2, 3),
         'y': _repeat(4, 3),
         'x_plus_y': _repeat(6, 3)}
    )
    assert actual.equals(expected), "mutate across failed"

def test_mutate_constant():
    """Can add a constant value without tp.lit"""
    df = tp.tibble({'x': _repeat(1, 3), 'y': _repeat(2, 3)})
    actual = df.mutate(z = "z")
    expected = tp.tibble(
        x = _repeat(1, 3),
        y = _repeat(2, 3),
        z = _repeat('z', 3)
    )
    assert actual.equals(expected), "mutate failed"

def test_names():
    """Can get column names"""
    df = tp.tibble({'x': _repeat(1, 3), 'y': _repeat(2, 3)})
    assert df.names == ['x', 'y'], "names failed"

def test_ncol():
    """Can number of columns"""
    df = tp.tibble({'x': _repeat(1, 3), 'y': _repeat(2, 3)})
    assert df.ncol == 2, "ncol failed"

def test_nrow():
    """Can number of rows"""
    df = tp.tibble({'x': _repeat(1, 3), 'y': _repeat(2, 3)})
    assert df.nrow == 3, "nrow failed"

def test_pivot_longer1():
    "Can pivot all (unspecified) cols to long"
    df = tp.tibble({'x': [1, 2], 'y': [3, 4]})
    actual = df.pivot_longer()
    expected = tp.tibble({'name': ['x', 'x', 'y', 'y'], 'value': range(1, 5)})
    assert actual.equals(expected), "unspecified pivot_longer failed"
    assert type(actual) == tp.tibble, "pivot_longer didn't return a tibble"

def test_pivot_longer2():
    """Can pivot all (specified) cols to long"""
    df = tp.tibble({'x': [1, 2], 'y': [3, 4]})
    actual = df.pivot_longer(['x', 'y'])
    expected = tp.tibble({'name': ['x', 'x', 'y', 'y'], 'value': range(1, 5)})
    assert actual.equals(expected), "specified pivot_longer failed"

def test_pivot_wider1():
    """Can pivot all cols to wide"""
    df = tp.tibble({'label': ['x', 'y', 'z'], 'val': range(1, 4)})
    actual = df.pivot_wider(names_from = 'label', values_from = 'val').select('x', 'y', 'z')
    expected = tp.tibble({'x': [1], 'y': [2], 'z': [3]})
    assert actual.equals(expected), "pivot_wider all cols failed"
    assert type(actual) == tp.tibble, "pivot_wider didn't return a tibble"

def test_pivot_wider2():
    """Can pivot cols to wide with id col"""
    df = tp.tibble({'id': _repeat(1, 3), 'label': ['x', 'y', 'z'], 'val': range(1, 4)})
    actual = df.pivot_wider(names_from = 'label', values_from = 'val').select('id', 'x', 'y', 'z')
    expected = tp.tibble({'id': [1], 'x': [1], 'y': [2], 'z': [3]})
    assert actual.equals(expected), "pivot_wider with id failed"

def test_pivot_wider3():
    """Can pivot cols to wide with values filled"""
    df = tp.tibble({'id': _repeat(1, 3), 'label': ['x', 'y', 'z'], 'val': range(1, 4)})
    actual = (
        df.pivot_wider(names_from = 'label', values_from = 'id', values_fill = 0)
        .select('val', 'x', 'y', 'z').arrange('val')
    )
    expected = tp.tibble({'val': [1, 2, 3], 'x': [1, 0, 0], 'y': [0, 1, 0], 'z': [0, 0, 1]})
    assert actual.equals(expected), "pivot_wider with values filled failed"

def test_pivot_wider4():
    """Can pivot cols to wide with values filled - doesn't affect id col"""
    df = tp.tibble(id = [None, 2], var = ["x", "y"], val = [1, 2])
    actual = (
        df.pivot_wider(names_from = "var", values_from = "val", values_fill = 0)
        .select('id', 'x', 'y')
        .arrange('y')
    )
    expected = tp.tibble({'id': [None, 2], 'x': [1, 0], 'y': [0, 2]})
    assert actual.equals(expected), "pivot_wider with values filled failed"

def test_print():
    """Printing doesn't alter class of df"""
    df = tp.tibble(x = range(3), y = range(3))
    repr(df)
    print(df)
    assert isinstance(df, tp.tibble), "Printing failed"

def test_pull():
    """Can use pull"""
    df = tp.tibble({'x': _repeat(1, 3), 'y': _repeat(2, 3)})
    actual = df.pull('x')
    expected = df.to_polars().get_column('x')
    assert actual.equals(expected), "pull failed"

def test_relocate_before():
    """Can relocate before columns"""
    df = tp.tibble({'x': range(3), 'y': range(3), 'z': range(3)})
    actual = df.relocate('y', 'z', before = 'x')
    expected = df.select('y', 'z', 'x')
    assert actual.equals(expected), "relocate before failed"
    assert type(actual) == tp.tibble, "relocate didn't return a tibble"

def test_relocate_after():
    """Can relocate after columns"""
    df = tp.tibble({'x': range(3), 'y': range(3), 'z': range(3)})
    actual = df.relocate('z', 'y', after = 'x')
    expected = df.select('x', 'z', 'y')
    assert actual.equals(expected), "relocate after failed"

def test_relocate_empty():
    """Can relocate to the beginning"""
    df = tp.tibble({'x': range(3), 'y': range(3), 'z': range(3)})
    actual = df.relocate('z', 'y')
    expected = df.select('z', 'y', 'x')
    assert actual.equals(expected), "relocate to the beginning failed"

def test_rename_dplyr_kwargs():
    """Can rename - dplyr interface (kwargs)"""
    df = tp.tibble({'x': range(3), 'y': range(3), 'z': range(3)})
    actual = df.rename(new_x = 'x', new_y = 'y')
    expected = tp.tibble({'new_x': range(3), 'new_y': range(3), 'z': range(3)})
    assert actual.equals(expected), "dplyr rename failed"
    assert type(actual) == tp.tibble, "rename didn't return a tibble"

def test_rename_dplyr_strings():
    """Can rename - dplyr interface (strings)"""
    df = tp.tibble({'x': range(3), 'y': range(3), 'z': range(3)})
    actual = df.rename('new_x', 'x', 'new_y', 'y')
    expected = tp.tibble({'new_x': range(3), 'new_y': range(3), 'z': range(3)})
    assert actual.equals(expected), "dplyr rename failed"

def test_rename_pandas():
    """Can rename - pandas interface"""
    df = tp.tibble({'x': range(3), 'y': range(3), 'z': range(3)})
    actual = df.rename({'x': 'new_x', 'y': 'new_y'})
    expected = tp.tibble({'new_x': range(3), 'new_y': range(3), 'z': range(3)})
    assert actual.equals(expected), "pandas rename failed"

def test_replace_null():
    """Can replace nulls"""
    df = tp.tibble(x = [0, None], y = [None, None])
    actual = df.replace_null(dict(x = 1, y = 2))
    expected = tp.tibble(x = [0, 1], y = [2, 2])
    assert actual.equals(expected), "replace_null method failed"
    assert type(actual) == tp.tibble, "replace_null didn't return a tibble"

def test_replace_fill_missing_labels_nested():
    """Can replace partial value labels with original values"""
    df = tp.tibble({'x': [1, 2, 3]})
    actual = df.replace({'x': {1: 'a', 2: 'b'}})
    expected = tp.tibble({'x': ['a', 'b', '3']})
    assert actual.equals(expected), "replace partial labels failed"
    assert type(actual) == tp.tibble, "replace didn't return a tibble"

def test_replace_fill_missing_labels_flat():
    """Can replace partial value labels with pandas-style mapping"""
    df = tp.tibble({'x': [1, 2, 3], 'y': [4, 5, 6]})
    actual = df.replace({1: 'a', 2: 'b'})
    expected = tp.tibble({'x': ['a', 'b', '3'], 'y': [4, 5, 6]})
    assert actual.equals(expected), "flat replace partial labels failed"

def test_replace_without_fill_missing_labels():
    """Can keep old replace behavior when label filling is disabled"""
    df = tp.tibble({'x': [1, 2, 3]})
    actual = df.replace({'x': {1: 10, 2: 20}}, fill_missing_labels=False)
    expected = tp.tibble({'x': [10, 20, 3]})
    assert actual.equals(expected), "replace without partial label fill failed"

def test_set_names():
    """Can set_names"""
    df = tp.tibble(x = range(3), y = range(3))
    actual = df.set_names(['a', 'b'])
    expected = tp.tibble(a = range(3), b = range(3))
    assert actual.equals(expected), "set_names failed"
    assert type(actual) == tp.tibble, "set_names didn't return a tibble"

def test_select():
    """Can select columns"""
    df = tp.tibble({'x': range(3), 'y': range(3), 'z': range(3)})
    actual = df.select('x', 'z')
    expected = df[['x', 'z']]
    assert actual.equals(expected), "select failed"
    assert type(actual) == tp.tibble, "select didn't return a tibble"

def test_separate():
    """Can separate"""
    df = tp.tibble(x = ['a_a', 'b_b', 'c_c'])
    actual = df.separate('x', into = ['left', 'right']).arrange('left')
    expected = tp.tibble(left = ['a', 'b', 'c'], right = ['a', 'b', 'c'])
    assert actual.equals(expected), "separate failed"
    assert type(actual) == tp.tibble, "separate didn't return a tibble"

def test_slice():
    """Can slice"""
    df = tp.tibble({'x': range(3), 'y': ['a', 'a', 'b']})
    actual = df.slice(0, 2)
    expected = tp.tibble({'x': [0, 2], 'y': ['a', 'b']})
    assert actual.equals(expected), "slice failed"
    assert type(actual) == tp.tibble, "slice didn't return a tibble"

def test_slice_head():
    """Can slice_head"""
    df = tp.tibble({'x': range(3), 'y': ['a', 'a', 'b']})
    actual = df.slice_head(2)
    expected = tp.tibble({'x': [0, 1], 'y': ['a', 'a']})
    assert actual.equals(expected), "slice_head failed"
    assert type(actual) == tp.tibble, "slice_head didn't return a tibble"

def test_slice_tail():
    """Can slice_tail by group"""
    df = tp.tibble({'x': range(3), 'y': ['a', 'a', 'b']})
    actual = df.slice_tail(2)
    expected = tp.tibble({'x': [1, 2], 'y': ['a', 'b']})
    assert actual.equals(expected), "slice_tail failed"
    assert type(actual) == tp.tibble, "slice_tail didn't return a tibble"

def test_summarise():
    """Can use summarise alias"""
    df = tp.tibble({'x': range(3), 'y': range(3), 'z': range(3)})
    actual = df.summarise(avg_x = col('x').mean())
    expected = tp.tibble({'avg_x': [1]})
    assert actual.equals(expected), "summarise failed"

def test_summarize():
    """Can use summarize"""
    df = tp.tibble({'x': range(3), 'y': range(3), 'z': range(3)})
    actual = df.summarize(avg_x = col('x').mean())
    expected = tp.tibble({'avg_x': [1]})
    assert actual.equals(expected), "ungrouped summarize failed"
    assert type(actual) == tp.tibble, "summarize didn't return a tibble"

def test_summarize_grouped():
    """Can use summarize by group"""
    df = tp.tibble({'x': range(3), 'y': range(3), 'z': ['a', 'a', 'b']})
    actual = df.summarize(avg_x = col('x').mean(), by = 'z').arrange('z')
    expected = tp.tibble(z = ['a', 'b'], avg_x = [.5, 2])
    assert actual.equals(expected), "grouped summarize failed"

def test_summarize_across():
    """Can use summarize_across"""
    df = tp.tibble(x = range(3), y = range(3), z = range(3))
    actual = df.summarize(tp.across(['x', 'y'], tp.max, names_prefix = "max_"),
                          avg_x = col('x').mean())
    expected = tp.tibble({'max_x': [2], 'max_y': [2], 'avg_x': [1]})
    assert actual.equals(expected), "ungrouped summarize across failed"

def test_to_dict():
    """Can convert to a dictionary"""
    df = tp.tibble({'x': range(3), 'y': range(3)})
    assert type(df.to_dict()) == dict

def test_to_polars():
    """Can convert to a polars DataFrame"""
    df = tp.tibble({'x': range(3), 'y': range(3), 'z': range(3)})
    assert isinstance(df.to_polars(), pl.DataFrame), "to_polars failed"

def test_unite():
    """Can unite columns"""
    df = tp.tibble(a = ["a", "a", "a"], b = ["b", "b", "b"], c = range(3))
    actual = df.unite("new_col", ["a", "b"])
    expected = tp.tibble(new_col = ["a_b"] * 3, c = range(3))
    assert actual.equals(expected), "unite failed"
    assert type(actual) == tp.tibble, "unite didn't return a tibble"

def test_funs_in_a_row():
    """Tests if shallow copy is working properly"""
    df = tp.tibble(x = range(3), y = range(3), z = range(3))
    df.distinct()
    df.drop('x')
    df.drop_null()
    df.filter(col('x') < 7)
    df.head()
    df.mutate(col('x') * 2)
    df.relocate('y', before = 'x')
    df.rename({'x': 'new_x'})
    df.select('x', 'y')
    df.slice(1)
    df.slice_head()
    df.slice_tail()
    df.tail()
    df.arrange('x', 'y')
    assert True, "Functions in a row failed"


_TESTED_TIBBLE_METHODS = {
    "arrange", "bind_cols", "bind_rows", "clone", "count", "crossing",
    "distinct", "drop", "drop_null", "equals", "fill", "filter",
    "full_join", "glimpse", "group_by", "head", "inner_join", "iterrows",
    "left_join", "mutate", "names", "ncol", "nest", "nrow",
    "pivot_longer", "pivot_wider", "print", "pull", "relevel",
    "relocate", "rename", "replace", "replace_null", "save_data",
    "select", "separate", "set_names", "slice", "slice_head",
    "slice_tail", "summarise", "summarize", "tail", "tab", "to_csv",
    "to_dict", "to_dta", "to_excel", "to_latex", "to_pandas",
    "to_parquet", "to_polars", "unite", "unnest",
    "colnames", "descriptive_statistics", "freq",
}


def test_all_public_tibble_methods_are_covered():
    public_methods = {
        name for name, member in tp.tibble.__dict__.items()
        if not name.startswith("_")
        and (inspect.isfunction(member) or isinstance(member, property))
    }
    assert public_methods - _TESTED_TIBBLE_METHODS == set()


def test_equals_checks_null_equality_option():
    df1 = tp.tibble(x=[1, None])
    df2 = tp.tibble(x=[1, None])
    assert df1.equals(df2)
    assert not df1.equals(df2, null_equal=False)


def test_distinct_keep_all_false():
    df = tp.tibble(x=["a", "a", "b"], y=[1, 2, 3])
    actual = df.distinct("x", keep_all=False).arrange("x")
    expected = tp.tibble(x=["a", "b"])
    assert actual.equals(expected)


def test_head_and_tail_aliases():
    df = tp.tibble(x=range(4), group=["a", "a", "b", "b"])
    assert df.head(2).equals(tp.tibble(x=[0, 1], group=["a", "a"]))
    assert df.tail(2).equals(tp.tibble(x=[2, 3], group=["b", "b"]))
    actual = df.head(1, by="group").arrange("group")
    expected = tp.tibble(x=[0, 2], group=["a", "b"])
    assert actual.equals(expected)


def test_fill_directions_and_grouping():
    df = tp.tibble(group=["a", "a", "b", "b"], x=[None, 1, None, 2])
    actual = df.fill("x", direction="up", by="group").arrange("group", "x")
    expected = tp.tibble(group=["a", "a", "b", "b"], x=[1, 1, 2, 2])
    assert actual.equals(expected)

    df2 = tp.tibble(x=[None, 1, None])
    assert df2.fill("x", direction="downup").equals(tp.tibble(x=[1, 1, 1]))


def test_join_with_explicit_keys_and_suffix():
    df1 = tp.tibble(left_id=[1, 2], value=["left-a", "left-b"])
    df2 = tp.tibble(right_id=[2, 3], value=["right-b", "right-c"])
    actual = df1.inner_join(
        df2,
        left_on="left_id",
        right_on="right_id",
        suffix="_other",
    )
    expected = tp.tibble(left_id=[2], value=["left-b"], value_other=["right-b"])
    assert actual.equals(expected)


def test_pivot_longer_custom_names_and_pull_default():
    df = tp.tibble(id=[1, 2], a=[10, 20], b=[30, 40])
    actual = df.pivot_longer(["a", "b"], names_to="metric", values_to="amount")
    expected = tp.tibble(
        id=[1, 2, 1, 2],
        metric=["a", "a", "b", "b"],
        amount=[10, 20, 30, 40],
    )
    assert actual.equals(expected)
    assert actual.pull().equals(actual.pull("amount"))


def test_relevel_preserves_ordered_factor_in_pandas():
    df = tp.tibble(x=["a", "b", "c", "a"])
    actual = df.relevel("x", "b")
    assert actual.pull("x").cat.get_categories().to_list()[0] == "b"

    pdf = actual.to_pandas()
    assert isinstance(pdf, pd.DataFrame)
    assert list(pdf["x"].cat.categories)[0] == "b"
    assert pdf["x"].cat.ordered


def test_rename_regex_and_tolower():
    df = tp.tibble(ABC=[1], DEF=[2])
    actual = df.rename({"^A": "x_"}, regex=True).rename(tolower=True)
    expected = tp.tibble({"x_bc": [1], "def": [2]})
    assert actual.equals(expected)


def test_replace_null_scalar_values():
    df = tp.tibble(name=["a", None], score=[None, 2], other=[None, 3.5])
    actual = df.replace_null("missing").replace_null(0)
    expected = tp.tibble(name=["a", "missing"], score=[0, 2], other=[0.0, 3.5])
    assert actual.equals(expected)


def test_select_dict_set_and_selector():
    df = tp.tibble(a=[1], b=[2], label=["x"])
    assert df.select({"a": "alpha"}, {"b"}).equals(tp.tibble(alpha=[1], b=[2]))
    assert df.select(pl.selectors.numeric()).equals(tp.tibble(a=[1], b=[2]))


def test_separate_and_unite_keep_source_columns():
    df = tp.tibble(x=["a-1", "b-2"], y=["z", "z"])
    separated = df.separate("x", into=["letter", "number"], sep="-", remove=False)
    assert separated.equals(
        tp.tibble(x=["a-1", "b-2"], y=["z", "z"], letter=["a", "b"], number=["1", "2"])
    )

    united = separated.unite("joined", ["letter", "number"], sep=":", remove=False)
    assert united.select("joined", "letter", "number").equals(
        tp.tibble(joined=["a:1", "b:2"], letter=["a", "b"], number=["1", "2"])
    )


def test_group_by_returns_grouped_tibble():
    grouped = tp.tibble(group=["a", "a", "b"], x=[1, 2, 3]).group_by("group")
    assert isinstance(grouped, tp.TibbleGroupBy)
    actual = grouped.summarize(total=col("x").sum()).arrange("group")
    expected = tp.tibble(group=["a", "b"], total=[3, 3])
    assert actual.equals(expected)


def test_nest_creates_tibble_objects_and_unnest_round_trips():
    df = tp.tibble(group=["a", "a", "b"], x=[1, 2, 3], y=["u", "v", "w"])
    nested = df.nest("group").arrange("group")

    assert nested.names == ["group", "data"]
    assert nested.pull("data").dtype == pl.Object
    assert isinstance(nested.pull("data")[0], tp.tibble)
    assert nested.pull("data")[0].equals(tp.tibble(x=[1, 2], y=["u", "v"]))

    actual = nested.unnest("data").arrange("group", "x")
    assert actual.equals(df.arrange("group", "x"))


def test_nest_string_by_does_not_drop_substring_columns():
    df = tp.tibble(id=[1, 1], i=[10, 20], value=["a", "b"])
    nested = df.nest("id")
    assert nested.pull("data")[0].names == ["i", "value"]


def test_nest_key_data_and_names_sep():
    df = tp.tibble(id=[1, 1], data_x=[10, 20], data_y=["a", "b"], z=[0, 0])
    nested = df.nest("id", data=["data_x", "data_y"], key="data", names_sep="_")

    assert nested.names == ["id", "data"]
    assert nested.pull("data")[0].equals(tp.tibble(x=[10, 20], y=["a", "b"]))


def test_nest_multiple_group_columns():
    df = tp.tibble(group=["a", "a", "a"], subgroup=[1, 1, 2], x=[10, 20, 30])
    actual = df.nest(["group", "subgroup"], key="rows").arrange("subgroup")

    assert actual.names == ["group", "subgroup", "rows"]
    assert actual.pull("rows")[0].equals(tp.tibble(x=[10, 20]))
    assert actual.pull("rows")[1].equals(tp.tibble(x=[30]))


def test_crossing_expands_all_combinations():
    df = tp.tibble(id=[1, 2])
    actual = df.crossing(letter=["a", "b"]).arrange("id", "letter")
    expected = tp.tibble(id=[1, 1, 2, 2], letter=["a", "b", "a", "b"])
    assert actual.equals(expected)


def test_colnames_regex_and_type():
    df = tp.tibble(score_1=[1], score_2=[2.0], label=["x"])
    assert set(df.colnames(regex="score")) == {"score_1", "score_2"}
    assert set(df.colnames(type="numeric")) == {"score_1", "score_2"}


def test_iterrows_yields_named_rows():
    rows = list(tp.tibble(x=[1, 2], y=["a", "b"]).iterrows())
    assert rows == [{"x": 1, "y": "a"}, {"x": 2, "y": "b"}]


def test_descriptive_statistics_includes_categorical_rows_and_type():
    df = tp.tibble(score=[1, 2, None], group=["a", "a", "b"])
    actual = df.descriptive_statistics(
        vars=["score", "group"],
        include_type=True,
    )

    assert {"Variable", "N", "Mean", "Type"}.issubset(set(actual.names))
    assert set(actual.pull("Type").to_list()) == {"Num", "Cat"}
    assert "group (a)" in actual.pull("Variable").to_list()


def test_freq_supports_weights():
    df = tp.tibble(choice=["yes", "no", "yes"], weight=[2.0, 1.0, 3.0])
    actual = df.freq("choice", weights="weight").arrange("choice")

    assert actual.pull("choice").to_list() == ["no", "yes"]
    assert actual.pull("N").to_list() == [1, 2]
    assert [round(x, 2) for x in actual.pull("Freq").to_list()] == [16.67, 83.33]


def test_tab_returns_contingency_table():
    df = tp.tibble(row=["a", "a", "b", "b"], column=["x", "y", "x", "x"])
    actual = df.tab("row", "column", stat="both")

    assert actual.names == ["row", "x", "y", "Total"]
    assert actual.filter(col("row") == "a").pull("x")[0] == "25.0 % (1)"
    assert actual.filter(col("row") == "Total").pull("Total")[0] == "100.0 % (4)"


def test_to_dict_as_lists():
    df = tp.tibble(x=[1, 2], y=["a", "b"])
    assert df.to_dict(as_series=False) == {"x": [1, 2], "y": ["a", "b"]}


def test_to_csv_writes_file(tmp_path):
    df = tp.tibble(x=[1, 2], y=["a", "b"])
    base = tmp_path / "data"
    df.to_csv(fn=str(base), ext="csv", silently=True, separator="|")

    assert (tmp_path / "data.csv").read_text().splitlines() == ["x|y", "1|a", "2|b"]


def test_to_parquet_writes_file(tmp_path):
    df = tp.tibble(x=[1, 2], y=["a", "b"])
    base = tmp_path / "data"
    df.to_parquet(fn=str(base), ext="parquet", silently=True)

    actual = tp.from_polars(pl.read_parquet(tmp_path / "data.parquet"))
    assert actual.equals(df)


def test_to_dta_writes_file(tmp_path):
    df = tp.tibble(x=[1, 2], y=["a", "b"])
    base = tmp_path / "data"
    df.to_dta(fn=str(base), ext="dta", silently=True, write_index=False)

    assert (tmp_path / "data.dta").exists()


def test_to_excel_writes_file(tmp_path):
    pytest.importorskip("xlsxwriter")
    df = tp.tibble(x=[1, 2], y=["a", "b"])
    base = tmp_path / "data"
    df.to_excel(fn=str(base), ext="xlsx", silently=True)

    assert (tmp_path / "data.xlsx").exists()


def test_to_latex_returns_string_and_writes_file(tmp_path):
    df = tp.tibble(x=[1, 2], y=["a", "b"])
    latex = df.to_latex(caption="Caption", label="tab:test", scale=False)
    assert "\\begin{table}" in latex
    assert "\\caption{Caption}" in latex

    out = tmp_path / "table.tex"
    assert df.to_latex(fn=str(out), scale=False) is None
    assert "\\begin{table}" in out.read_text()


def test_save_data_writes_requested_copies(tmp_path):
    df = tp.tibble(x=[1, 2], y=["a", "b"])
    df.save_data(str(tmp_path / "data.csv"), copies=["parquet"], silently=True)

    assert (tmp_path / "data.csv").exists()
    assert (tmp_path / "data.parquet").exists()
