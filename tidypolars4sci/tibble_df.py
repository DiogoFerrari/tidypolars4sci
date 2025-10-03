import polars as pl
import functools as ft
from .utils import (_as_list,
                    _col_expr,
                    _col_exprs,
                    _kwargs_as_exprs,
                    _mutate_cols,
                    _uses_by
                    )
from .funs import map
from .stringr import str_c
from .stats import *
from .reexports import *
from .type_conversion import *
from .helpers import everything, matches, DescCol, desc
import copy
from operator import not_
import numpy as np
import pandas as pd
import re
from itertools import chain
import warnings
warnings.filterwarnings("ignore", category=pl.exceptions.MapWithoutReturnDtypeWarning)

__all__ = [
    "tibble", "TibbleGroupBy",
    "from_pandas", "from_polars"
    ]

class tibble(pl.DataFrame):
    """
    A data frame object that provides methods familiar to R tidyverse users.
    """
    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def _constructor(self):
        # '''
        # This method ensures that the method tibble return an instance
        # of tibble, instead of a DataFrame
        # '''
        return self.__class__

    def _repr_html_(self):
        # """
        # Printing method for jupyter

        # Output rows and columns can be modified by setting the following ENVIRONMENT variables:

        # * POLARS_FMT_MAX_COLS: set the number of columns

        # * POLARS_FMT_MAX_ROWS: set the number of rows
        # """
        df = self.to_polars()
        return df._repr_html_()

    def __copy__(self):
        # Shallow copy
        # See: https://stackoverflow.com/a/51043609/13254470
        obj = type(self).__new__(self.__class__)
        obj.__dict__.update(self.__dict__)
        return obj

    def __getattribute__(self, attr):
        if attr in _polars_methods:
            raise AttributeError
        return pl.DataFrame.__getattribute__(self, attr)

    def __dir__(self):
        _tidypolars_methods = [
            'arrange', 'bind_cols', 'bind_rows', 'colnames', 'clone', 'count',
            'crossing',
            'distinct', 'drop', 'drop_null', 'head', 'fill', 'filter',
            'group_by', 
            'inner_join', 'left_join', 'mutate', 'names', 'nest',
            'nrow', 'ncol',
            'full_join', 'pivot_longer', 'pivot_wider', 'print',
            'pull', 'relocate', 'rename',
            'replace',
            'replace_null', 'select',
            'separate', 'set_names',
            'slice', 'slice_head', 'slice_tail', 'summarize', 'tail',
            'to_pandas', 'to_polars', 'unnest', 'write_csv', 'write_parquet'
        ]
        return _tidypolars_methods
    
    def arrange(self, *args):
        """
        Arrange/sort rows

        Parameters
        ----------
        *args : str
            Columns to sort by

        Examples
        --------
        >>> df = tp.tibble({'x': ['a', 'a', 'b'], 'y': range(3)})
        >>> # Arrange in ascending order
        >>> df.arrange('x', 'y')
        >>> # Arrange some columns descending
        >>> df.arrange(tp.desc('x'), 'y')

        Returns
        ------- 
        tibble
            Original tibble orderd by *args
        """
        exprs = _as_list(args)
        desc = [True if isinstance(expr, DescCol) else False for expr in exprs]
        return super()\
            .sort(exprs, descending = desc, nulls_last=True)\
            .pipe(from_polars)

    def bind_cols(self, *args):
        """
        Bind data frames by columns

        Parameters
        ----------
        *args : tibble
            Data frame to bind

        Returns
        ------- 
        tibble
            The original tibble with added columns 
            from the other tibble specified in *args

        Examples
        --------
        >>> df1 = tp.tibble({'x': ['a', 'a', 'b'], 'y': range(3)})
        >>> df2 = tp.tibble({'a': ['c', 'c', 'c'], 'b': range(4, 7)})
        >>> df1.bind_cols(df2)
        """
        frames = _as_list(args)
        out = self.to_polars()
        for frame in frames:
            out = out.hstack(frame)
        return out.pipe(from_polars)
    
    def bind_rows(self, *args):
        """
        Bind data frames by row

        Parameters
        ----------
        *args : tibble, list
            Data frames to bind by row

        Returns
        ------- 
        tibble
            The original tibble with added rows 
            from the other tibble specified in *args

        Examples
        --------
        >>> df1 = tp.tibble({'x': ['a', 'a', 'b'], 'y': range(3)})
        >>> df2 = tp.tibble({'x': ['c', 'c', 'c'], 'y': range(4, 7)})
        >>> df1.bind_rows(df2)
        """
        frames = _as_list(args)
        out = pl.concat([self, *frames], how = "diagonal")
        return out.pipe(from_polars)

    def clone(self):
        """
        Very cheap deep clone
        """
        return super().clone().pipe(from_polars)

    def count(self, *args, sort = False, name = 'n'):
        """
        Returns row counts of the dataset. 
        If bare column names are provided, count() returns counts by group.

        Parameters
        ----------
        *args : str, Expr
            Columns to group by
        sort : bool
            Should columns be ordered in descending order by count
        name : str
            The name of the new column in the output. If omitted, it will default to "n".

        Returns
        ------- 
        tibble
            If no agument is provided, just return the nomber of rows.
            If column names are provided, it will count the unique 
            values across columns

        Examples
        --------
        >>> df = tp.tibble({'a': [1, 1, 2, 3],
        ...:                 'b': ['a', 'a', 'b', 'b']})
        >>> df.count()
        shape: (1, 1)
        ┌─────┐
        │   n │
        │ u32 │
        ╞═════╡
        │   4 │
        └─────┘
        >>> df.count('a', 'b')
        shape: (3, 3)
        ┌─────────────────┐
        │   a   b       n │
        │ i64   str   u32 │
        ╞═════════════════╡
        │   1   a       2 │
        │   2   b       1 │
        │   3   b       1 │
        └─────────────────┘
        """
        args = _as_list(args)
        
        out = self.summarize(pl.len().alias(name), by = args)

        if sort == True:
            out = out.arrange(desc(name))

        return out

    def distinct(self, *args, keep_all = True):
        """
        Select distinct/unique rows

        Parameters
        ----------
        *args : str, Expr
            Columns to find distinct/unique rows

        keep_all : boll
            If True, keep all columns. Otherwise, return
            only the ones used to select the distinct rows.

        Returns
        ------- 
        tibble
            Tibble after removing the repeated rows based on *args

        Examples
        --------
        >>> df = tp.tibble({'a': range(3), 'b': ['a', 'a', 'b']})
        >>> df.distinct()
        >>> df.distinct('b')
        """
        args = _as_list(args)
        # 
        if len(args) == 0:
            df = super().unique()
        else:
            df = super().unique(args)
        if not keep_all and len(args) > 0:
            df = df.select(args)
        return df.pipe(from_polars)

    def drop(self, *args):
        """
        Drop unwanted columns

        Parameters
        ----------
        *args : str
            Columns to drop

        Returns
        ------- 
        tibble
            Tibble with columns in *args dropped

        Examples
        --------
        >>> df.drop('x', 'y')
        """
        args = _as_list(args)
        drop_cols = self.select(args).names
        return super().drop(drop_cols).pipe(from_polars)

    def drop_null(self, *args):
        """
        Drop rows containing missing values

        Parameters
        ----------
        *args : str
            Columns to drop nulls from (defaults to all)

        Returns
        ------- 
        tibble
            Tibble with rows in *args with missing values dropped

        Examples
        --------
        >>> df = tp.tibble(x = [1, None, 3], y = [None, 'b', 'c'], z = range(3)}
        >>> df.drop_null()
        >>> df.drop_null('x', 'y')
        """
        args = _as_list(args)
        if len(args) == 0:
            out = super().drop_nulls()
        else:
            out = super().drop_nulls(args)
        return out.pipe(from_polars)
    
    def equals(self, other, null_equal = True):
        """
        Check if two tibbles are equal
        """
        df = self.to_polars()
        other = other.to_polars()
        return df.equals(other, null_equal = null_equal)
    
    def head(self, n = 5, *, by = None):
        """
        Alias for `.slice_head()`
        """
        return self.slice_head(n, by = by)

    def fill(self, *args, direction = 'down', by = None):
        """
        Fill in missing values with previous or next value

        Parameters
        ----------
        *args : str
            Columns to fill
        direction : str
            Direction to fill. One of ['down', 'up', 'downup', 'updown']
        by : str, list
            Columns to group by

        Returns
        ------- 
        tibble
            Tibble with missing values filled

        Examples
        --------
        >>> df = tp.tibble({'a': [1, None, 3, 4, 5],
        ...                 'b': [None, 2, None, None, 5],
        ...                 'groups': ['a', 'a', 'a', 'b', 'b']})
        >>> df.fill('a', 'b')
        >>> df.fill('a', 'b', by = 'groups')
        >>> df.fill('a', 'b', direction = 'downup')
        """
        args = _as_list(args)
        if len(args) == 0: return self
        args = _col_exprs(args)
        options = {'down': 'forward', 'up': 'backward'}
        if direction in ['down', 'up']:
            direction = options[direction]
            exprs = [arg.fill_null(strategy = direction) for arg in args]
        elif direction == 'downup':
            exprs = [
                arg.fill_null(strategy = 'forward')
                .fill_null(strategy = 'backward')
                for arg in args
            ]
        elif direction == 'updown':
            exprs = [
                arg.fill_null(strategy = 'backward')
                .fill_null(strategy = 'forward')
                for arg in args
            ]
        else:
            raise ValueError("direction must be one of down, up, downup, or updown")

        return self.mutate(*exprs, by = by)

    def filter(self, *args,
               by = None):
        """
        Filter rows on one or more conditions

        Parameters
        ----------
        *args : Expr
            Conditions to filter by
        by : str, list
            Columns to group by

        Returns
        ------- 
        tibble
            A tibble with rows that match condition.

        Examples
        --------
        >>> df = tp.tibble({'a': range(3), 'b': ['a', 'a', 'b']})
        >>> df.filter(col('a') < 2, col('b') == 'a')
        >>> df.filter((col('a') < 2) & (col('b') == 'a'))
        >>> df.filter(col('a') <= tp.mean(col('a')), by = 'b')
        """
        args = _as_list(args)
        exprs = ft.reduce(lambda a, b: a & b, args)

        if _uses_by(by):
            out = super().group_by(by).map_groups(lambda x: x.filter(exprs))
        else:
            out = super().filter(exprs)
        
        return out.pipe(from_polars)

    def inner_join(self, df, left_on = None, right_on = None, on = None, suffix = '_right'):
        """
        Perform an inner join

        Parameters
        ----------
        df : tibble
            Lazy DataFrame to join with.
        left_on : str, list
            Join column(s) of the left DataFrame.
        right_on : str, list
            Join column(s) of the right DataFrame.
        on: str, list
            Join column(s) of both DataFrames. If set, `left_on` and `right_on` should be None.
        suffix : str
            Suffix to append to columns with a duplicate name.

        Returns
        ------- 
        tibble
            A tibble with intersection of cases in the original and
            df tibbles.

        Examples
        --------
        >>> df1.inner_join(df2)
        >>> df1.inner_join(df2, on = 'x')
        >>> df1.inner_join(df2, left_on = 'left_x', right_on = 'x')
        """
        if (left_on == None) & (right_on == None) & (on == None):
            on = list(set(self.names) & set(df.names))
        return super().join(df, on, 'inner',
                            left_on = left_on,
                            right_on= right_on,
                            suffix= suffix).pipe(from_polars)

    def left_join(self, df, left_on = None, right_on = None, on = None, suffix = '_right'):
        """
        Perform a left join

        Parameters
        ----------
        df : tibble
            Lazy DataFrame to join with.
        left_on : str, list
            Join column(s) of the left DataFrame.
        right_on : str, list
            Join column(s) of the right DataFrame.
        on: str, list
            Join column(s) of both DataFrames. If set, `left_on` and `right_on` should be None.
        suffix : str
            Suffix to append to columns with a duplicate name.

        Returns
        ------- 
        tibble
             The original tibble with added columns from tibble df if
             they match columns in the original one. Columns to match
             on are given in the function parameters.

        Examples
        --------
        >>> df1.left_join(df2)
        >>> df1.left_join(df2, on = 'x')
        >>> df1.left_join(df2, left_on = 'left_x', right_on = 'x')
        """
        if (left_on == None) & (right_on == None) & (on == None):
            on = list(set(self.names) & set(df.names))
        return super().join(df, on, 'left',  left_on = left_on, right_on= right_on, suffix= suffix).pipe(from_polars)

    def mutate(self, *args, by = None, **kwargs):
        """
        Add or modify columns

        Parameters
        ----------
        *args : Expr
            Column expressions to add or modify
        by : str, list
            Columns to group by
        **kwargs : Expr
            Column expressions to add or modify

        Returns
        ------- 
        tibble
            Original tibble with new column created.
        
        Examples
        --------
        >>> df = tp.tibble({'a': range(3), 'b': range(3), c = ['a', 'a', 'b']})
        >>> df.mutate(double_a = col('a') * 2,
        ...           a_plus_b = col('a') + col('b'))
        >>> df.mutate(row_num = row_number(), by = 'c')
        """
        exprs = _as_list(args) + _kwargs_as_exprs(kwargs)

        out = self.to_polars()

        if _uses_by(by):
            out = out.group_by(by).map_groups(lambda x: _mutate_cols(x, exprs))
        else:
            out = _mutate_cols(out, exprs)
            
        return out.pipe(from_polars)

    @property
    def names(self):
        """
        Get column names

        Returns
        ------- 
        list
            Names of the columns
        
        Examples
        --------
        >>> df.names
        """
        return super().columns

    @property
    def ncol(self):
        """
        Get number of columns

        Returns
        ------- 
        int
            Number of columns
        
        Examples
        --------
        >>> df.ncol
        """
        return super().shape[1]

    @property
    def nrow(self):
        """
        Get number of rows
        
        Returns
        ------- 
        int
            Number of rows

        Examples
        --------
        >>> df.nrow
        """
        return super().shape[0]

    def full_join(self, df, left_on = None, right_on = None, on = None, suffix: str = '_right'):
        """
        Perform an full join

        Parameters
        ----------
        df : tibble
            Lazy DataFrame to join with.
        left_on : str, list
            Join column(s) of the left DataFrame.
        right_on : str, list
            Join column(s) of the right DataFrame.
        on: str, list
            Join column(s) of both DataFrames. If set, `left_on` and `right_on` should be None.
        suffix : str
            Suffix to append to columns with a duplicate name.

        Returns
        ------- 
        tibble
            Union between the original and the df tibbles. The
            rows that don't match in one of the tibbles will be
            completed with missing values.

        Examples
        --------
        >>> df1.full_join(df2)
        >>> df1.full_join(df2, on = 'x')
        >>> df1.full_join(df2, left_on = 'left_x', right_on = 'x')
        """
        if (left_on == None) & (right_on == None) & (on == None):
            on = list(set(self.names) & set(df.names))
        return super().join(df, on, 'outer',
                            left_on = left_on,
                            right_on= right_on, suffix= suffix).pipe(from_polars)

    def pivot_longer(self,
                     cols = None,
                     names_to = "name",
                     values_to = "value"):
        """
        Pivot data from wide to long

        Parameters
        ----------
        cols : Expr
            List of the columns to pivot. Defaults to all columns.
        names_to : str
            Name of the new "names" column.
        values_to: str
            Name of the new "values" column

        Returns
        ------- 
        tibble
            Original tibble, but in long format.

        Examples
        --------
        >>> df = tp.tibble({'id': ['id1', 'id2'], 'a': [1, 2], 'b': [1, 2]})
        >>> df.pivot_longer(cols = ['a', 'b'])
        >>> df.pivot_longer(cols = ['a', 'b'], names_to = 'stuff', values_to = 'things')
        """
        if cols is None:
            cols = everything()
        if isinstance(cols, dict):
            cols = list(cols.keys())
            
        df_cols = pl.Series(self.names)
        value_vars = self.select(cols).names
        id_vars = df_cols.filter(df_cols.is_in(value_vars).not_()).to_list()
        out = super().melt(id_vars, value_vars, names_to, values_to)
        return out.pipe(from_polars)

    def pivot_wider(self,
                    names_from = 'name',
                    values_from = 'value',
                    id_cols = None,
                    values_fn = 'first', 
                    values_fill = None
                    ):
        """
        Pivot data from long to wide

        Parameters
        ----------
        names_from : str
            Column to get the new column names from.
        values_from : str
            Column to get the new column values from
        id_cols : str, list
            A set of columns that uniquely identifies each observation.
            Defaults to all columns in the data table except for the columns specified in
            `names_from` and `values_from`.
        values_fn : str
            Function for how multiple entries per group should be dealt with.
            Any of 'first', 'count', 'sum', 'max', 'min', 'mean', 'median', 'last'
        values_fill : str
            If values are missing/null, what value should be filled in.
            Can use: "backward", "forward", "mean", "min", "max", "zero", "one"

        Returns
        ------- 
        tibble
            Original tibble, but in wide format.

        Examples
        --------
        >>> df = tp.tibble({'id': [1, 1], 'variable': ['a', 'b'], 'value': [1, 2]})
        >>> df.pivot_wider(names_from = 'variable', values_from = 'value')
        """
        if id_cols == None:
            df_cols = pl.Series(self.names)
            from_cols = pl.Series(self.select(names_from, values_from).names)
            id_cols = df_cols.filter(df_cols.is_in(from_cols).not_()).to_list()

        no_id = len(id_cols) == 0

        if no_id:
            id_cols = '___id__'
            self = self.mutate(___id__ = pl.lit(1))

        out = (
            super()
            .pivot(index=id_cols, on=names_from, values=values_from, aggregate_function=values_fn)
            .pipe(from_polars)
        )

        if values_fill != None:
            new_cols = pl.Series(out.names)
            new_cols = new_cols.filter(~new_cols.is_in(id_cols))
            fill_exprs = [col(new_col).fill_null(values_fill) for new_col in new_cols]
            out = out.mutate(*fill_exprs)

        if no_id: out = out.drop('___id__')

        return out

    def pull(self, var = None):
        """
        Extract a column as a series

        Parameters
        ----------
        var : str
            Name of the column to extract. Defaults to the last column.

        Returns
        ------- 
        Series
            The series will contain the values of the column from `var`.

        Examples
        --------
        >>> df = tp.tibble({'a': range(3), 'b': range(3))
        >>> df.pull('a')
        """
        if var == None:
            var = self.names[-1]
        
        return super().get_column(var)

    def relevel(self, x, ref):
        """
        Change the reference level a string or factor and covert to factor

        Inputs
        ------
        x : str
            Variable name

        ref : str
           Reference level

        Returns
        ------- 
        tibble
            The original tibble with the column specified in `x` as
            an ordered factors, with first category specified in `ref`.
        """
        levels = self.pull(x).unique().to_list()
        relevels = [ref] + [l for l in levels if l != ref]
        self = self.mutate(**{x : as_factor(x, relevels)})
        return self
    
    def relocate(self, *args, before = None, after = None):
        """
        Move a column or columns to a new position

        Parameters
        ----------
        *args : str, Expr
            Columns to move

        Returns
        ------- 
        tibble
            Original tibble with columns relocated.

        Examples
        --------
        >>> df = tp.tibble({'a': range(3), 'b': range(3), 'c': ['a', 'a', 'b']})
        >>> df.relocate('a', before = 'c')
        >>> df.relocate('b', after = 'c')
        """
        cols_all = pl.Series(self.names)
        locs_all = pl.Series(range(len(cols_all)))
        locs_dict = {k:v for k,v in zip(cols_all, locs_all)}
        locs_df = pl.DataFrame(locs_dict, orient = "row")

        cols_relocate = _as_list(args)
        locs_relocate = pl.Series(locs_df.select(cols_relocate).row(0))

        if (len(locs_relocate) == 0):
            return self

        uses_before = before != None
        uses_after = after != None

        if (uses_before & uses_after):
            raise ValueError("Cannot provide both before and after")
        elif (not_(uses_before) & not_(uses_after)):
            before = cols_all[0]
            uses_before = True

        if uses_before:
            before = locs_df.select(before).get_column(before)
            locs_start = locs_all.filter(locs_all < before)
        else:
            after = locs_df.select(after).get_column(after)
            locs_start = locs_all.filter(locs_all <= after)

        locs_start = locs_start.filter(~locs_start.is_in(locs_relocate))
        final_order = pl.concat([locs_start, locs_relocate, locs_all]).unique(maintain_order = True)
        final_order = cols_all[final_order].to_list()

        return self.select(final_order)
   
    def rename(self, columns=None, regex=False, tolower=False, strict=False):
        """
        Rename columns

        Parameters
        ----------
        columns : dict, default None
            Dictionary mapping of old and new names
            {<old name>:<new name>, ...}

        regex : bool, default False
            If True, uses regular expression replacement
            {<matched from>:<matched to>}

        tolower : bool, default False
            If True, convert all to lower case

        Returns
        ------- 
        tibble
            Original tibble with columns renamed.

        Examples
        --------
        >>> df = tp.tibble({'x': range(3), 't': range(3), 'z': ['a', 'a', 'b']})
        >>> df.rename({'x': 'new_x'}) 
        """
        assert isinstance(columns, dict) or columns is None,\
            "'columns' must be a dictionary or None."

        if columns is not None:
            if regex:
                self = self.__rename_regexp__(columns)
            else:
                self = super().rename(columns, strict=False).pipe(from_polars)

        if tolower:
            self = self.__rename_tolower__()
        return self

    def __rename_regexp__(self, mapping):
        pattern = next(iter(mapping))
        replacement = next(iter(mapping.values()))
        old = self.names
        new = [re.sub(pattern, replacement, col) for col in self.names]
        mapping = {o:n for o, n in zip(old, new)}
        return self.rename(mapping, regex=False)
        
    def __rename_tolower__(self):
        old = self.names
        new = [col.lower() for col in self.names]
        mapping = {o:n for o, n in zip(old, new)}
        return self.rename(mapping, regex=False)

    def replace_null(self, replace = None):
        """
        Replace null values

        Parameters
        ----------
        replace : dict
            Dictionary of column/replacement pairs

        Returns
        -------
        tibble
            Original tibble with missing/null values replaced.

        Examples
        --------
        >>> df = tp.tibble(x = [0, None], y = [None, None])
        >>> df.replace_null(dict(x = 1, y = 2))
        """
        if replace == None: return self
        if type(replace) != dict:
            ValueError("replace must be a dictionary of column/replacement pairs")
        replace_exprs = [col(key).fill_null(value) for key, value in replace.items()]
        return self.mutate(*replace_exprs)

    def separate(self, sep_col, into, sep = '_', remove = True):
        """
        Separate a character column into multiple columns

        Parameters
        ----------
        sep_col : str
            Column to split into multiple columns
        into : list
            List of new column names
        sep : str
            Separator to split on. Default to '_'
        remove : bool
            If True removes the input column from the output data frame

        Returns
        -------
        tibble
            Original tibble with a column splitted based on `sep`.

        Examples
        --------
        >>> df = tp.tibble(x = ['a_a', 'b_b', 'c_c'])
        >>> df.separate('x', into = ['left', 'right'])
        """
        into_len = len(into) - 1
        sep_df = (
            self
            .to_polars()
            .select(col(sep_col)
                    .str.split_exact(sep, into_len)
                    .alias("_seps")
                    .struct
                    .rename_fields(into))
            .unnest("_seps")
            .pipe(from_polars)
        )
        out = self.bind_cols(sep_df)
        if remove == True:
            out = out.drop(sep_col)
        return out

    def set_names(self, nm = None):
        """
        Change the column names of the data frame

        Parameters
        ----------
        nm : list
            A list of new names for the data frame

        Examples
        --------
        >>> df = tp.tibble(x = range(3), y = range(3))
        >>> df.set_names(['a', 'b'])
        """
        if nm == None: nm = self.names
        nm = _as_list(nm)
        rename_dict = {k:v for k, v in zip(self.names, nm)}
        return self.rename(rename_dict)
    
    def select(self, *args):
        """
        Select or drop columns

        Parameters
        ----------
        *args : str, list, dict, of combinations of them
            Columns to select. It can combine names, list of names,
            and a dict. If dict, it will rename the columns based
            on the dict.
            It also accepts tp.matches(<regex>) and tp.contains(<str>)

        Examples
        --------
        >>> df = tp.tibble({'a': range(3), 'b': range(3), 'abcba': ['a', 'a', 'b']})
        >>> df.select('a', 'b')
        >>> df.select(col('a'), col('b'))
        >>> df.select({'a': 'new name'}, tp.matches("c"))
        """
        # convert to list if dict.keys or dict.values are used
        cols_to_select = []
        cols_to_rename = {}
        for arg in args:
            if isinstance(arg, {}.keys().__class__) or\
               isinstance(arg, {}.values().__class__):
                cols_to_select += list(arg)

            elif isinstance(arg, dict):
                cols_to_select += [col for col,_ in arg.items()] 
                cols_to_rename |= arg 
                
            elif isinstance(arg, str):
                cols_to_select += [arg]
                
            elif isinstance(arg, list):
                cols_to_select += arg
                
            elif isinstance(arg, set):
                cols_to_select += list(arg)
        
        # # rename columns if dict is used
        # cols_dict = [d for d in args if isinstance(d, dict)]
        # if cols_dict:
        #     cols_dict = cols_dict[0]
        #     dict_list = list(cols_dict.values())
        #     self = self.rename(cols_dict)
        # else:
        #     dict_list = []
        
        # # collect str and list elements
        # cols_list = [c for c in args if isinstance(c, str) or isinstance(c, list)]
        # # flatten list
        # cols_list = list(chain.from_iterable((x if isinstance(x, list)
        #                                       else [x] for x in cols_list ))) 

        # # collect dict.keys() or dict.values()
        # cols_dict_keys   = [k for k in args if isinstance( k, type({}.keys()) )]
        # cols_dict_values = [k for k in args if isinstance( k, type({}.values()) )]

        # # collect set
        # cols_set = [s for s in args if isinstance(s, set)]
        # if cols_set:
        #     cols_set = list(cols_set[0])

        # cols = cols_list + dict_list + cols_dict_keys +cols_dict_values +cols_set 

        # remove non-existing columns
        cols_to_select = [col for col in cols_to_select 
                          if col in self.names 
                          or (col.startswith("^") and col.endswith("$"))] 
        # cols = [col for col in cols if col in self.names or
        #         (col.startswith("^") and col.endswith("$"))]
        
        cols = _col_exprs(cols_to_select)
        return super().select(cols).pipe(from_polars).rename(cols_to_rename)

    def slice(self, *args, by = None):
        """
        Grab rows from a data frame

        Parameters
        ----------
        *args : int, list
            Rows to grab
        by : str, list
            Columns to group by

        Examples
        --------
        >>> df = tp.tibble({'a': range(3), 'b': range(3), 'c': ['a', 'a', 'b']})
        >>> df.slice(0, 1)
        >>> df.slice(0, by = 'c')
        """
        rows = _as_list(args)
        if _uses_by(by):
            df = super(tibble, self).group_by(by).map_groups(lambda x: x.select(pl.all().gather(rows)))
        else:
            df = super(tibble, self).select(pl.all().gather(rows))
        return df.pipe(from_polars)

    def slice_head(self, n = 5, *, by = None):
        """
        Grab top rows from a data frame

        Parameters
        ----------
        n : int
            Number of rows to grab
        by : str, list
            Columns to group by

        Examples
        --------
        >>> df = tp.tibble({'a': range(3), 'b': range(3), 'c': ['a', 'a', 'b']})
        >>> df.slice_head(2)
        >>> df.slice_head(1, by = 'c')
        """
        col_order = self.names
        if _uses_by(by):
            df = super(tibble, self).group_by(by).head(n)
        else:
            df = super(tibble, self).head(n)
        df = df.select(col_order)
        return df.pipe(from_polars)

    def slice_tail(self, n = 5, *, by = None):
        """
        Grab bottom rows from a data frame

        Parameters
        ----------
        n : int
            Number of rows to grab
        by : str, list
            Columns to group by

        Examples
        --------
        >>> df = tp.tibble({'a': range(3), 'b': range(3), 'c': ['a', 'a', 'b']})
        >>> df.slice_tail(2)
        >>> df.slice_tail(1, by = 'c')
        """
        col_order = self.names
        if _uses_by(by):
            df = super(tibble, self).group_by(by).tail(n)
        else:
            df = super(tibble, self).tail(n)
        df = df.select(col_order)
        return df.pipe(from_polars)
    
    def summarise(self, *args,
                  by = None,
                  **kwargs):
        """Alias for `.summarize()`"""
        return self.summarize(*args, by = by, **kwargs)
    
    def summarize(self, *args,
                  by = None,
                  **kwargs):
        """
        Aggregate data with summary statistics

        Parameters
        ----------
        *args : Expr
            Column expressions to add or modify
        by : str, list
            Columns to group by
        **kwargs : Expr
            Column expressions to add or modify

        Returns
        -------
        tibble
            A tibble with the summaries


        Examples
        --------
        >>> df = tp.tibble({'a': range(3), 'b': range(3), 'c': ['a', 'a', 'b']})
        >>> df.summarize(avg_a = tp.mean(col('a')))
        >>> df.summarize(avg_a = tp.mean(col('a')),
        ...              by = 'c')
        >>> df.summarize(avg_a = tp.mean(col('a')),
        ...              max_b = tp.max(col('b')))
        """
        exprs = _as_list(args) + _kwargs_as_exprs(kwargs)
        if _uses_by(by):
            out = super(tibble, self).group_by(by).agg(exprs)
        else:
            out = super(tibble, self).select(exprs)
        return out.pipe(from_polars)

    def tail(self, n = 5, *, by = None):
        """Alias for `.slice_tail()`"""
        return self.slice_tail(n, by = by)

    def to_dict(self, *, as_series = True):
        """
        Aggregate data with summary statistics

        Parameters
        ----------
        as_series : bool
            If True - returns the dict values as Series
            If False - returns the dict values as lists

        Examples
        --------
        >>> df.to_dict()
        >>> df.to_dict(as_series = False)
        """
        return super().to_dict(as_series = as_series)

    def to_pandas(self):
        """
        Convert to a pandas DataFrame

        Examples
        --------
        >>> df.to_pandas()
        """
        # keep order of factors (pl.Enum)
        enum_columns = [col for col in self.names if self.pull(col).dtype == pl.Enum]
        res = self.to_polars().to_pandas()
        if enum_columns :
            for col in enum_columns:
                # Get unique categories in order of appearance
                categories_in_order = self.pull(col).cat.get_categories().to_list()
                # Convert the column to Categorical
                res[col] = pd.Categorical(
                    res[col],
                    categories=categories_in_order,
                    ordered=True
                )
        return res

    def to_polars(self):
        """
        Convert to a polars DataFrame

        Examples
        --------
        >>> df.to_polars()
        """
        self = copy.copy(self)
        self.__class__ = pl.DataFrame
        return self

    def unite(self, col = "_united", unite_cols = [], sep = "_", remove = True):
        """
        Unite multiple columns by pasting strings together

        Parameters
        ----------
        col : str
            Name of the new column
        unite_cols : list
            List of columns to unite
        sep : str
            Separator to use between values
        remove : bool
            If True removes input columns from the data frame

        Examples
        --------
        >>> df = tp.tibble(a = ["a", "a", "a"], b = ["b", "b", "b"], c = range(3))
        >>> df.unite("united_col", unite_cols = ["a", "b"])
        """
        if len(unite_cols) == 0:
            unite_cols = self.names
        else: 
            unite_cols = _col_exprs(unite_cols)
            unite_cols = self.select(unite_cols).names
        out = self.mutate(str_c(*unite_cols, sep = sep).alias(col))
        out = out.relocate(col, before = unite_cols[0])
        if remove == True:
            out = out.drop(unite_cols)
        return out
    
    def write_csv(self,
                  file = None,
                  has_headers = True,
                  sep = ','):
        """Write a data frame to a csv"""
        return super().write_csv(file, include_header = has_headers, separator = sep)

    def write_parquet(self,
                      file = str,
                      compression = 'snappy',
                      use_pyarrow = False,
                      **kwargs):
        """Write a data frame to a parquet"""
        return super().write_parquet(file, compression = compression, use_pyarrow = use_pyarrow, **kwargs)

    def group_by(self, group, *args, **kwargs):
        """
        Takes an existing tibble and converts it into a grouped tibble
        where operations are performed "by group". ungroup() happens
        automatically after the operation is performed.

        Parameters
        ---------- 
        group : str, list
            Variable names to group by.

        Returns
        -------
        Grouped tibble
            A tibble with values grouped by one or more columns.
        """
        res = TibbleGroupBy(self, group, maintain_order=True)
        return res
    
    def nest(self, by, *args, **kwargs):
        """
        creates a nested tibble

        Parameters
        ----------
        by : list, str
            Columns to nest on

        kwargs :
            data : list of column names
               columns to select to include in the nested data
               If not provided, include all columns except the ones
               used in 'by'

             key : str
               name of the resulting nested column. 

             names_sep : str
                If not provided (default), the names in the nested
                data will come from the former names. If a string,
                the new inner names in the nested dataframe will use
                the outer names with names_sep automatically stripped.
                This makes names_sep roughly
                symmetric between nesting and unnesting.

        Returns
        -------
        tibble
            The resulting tibble with have a column that contains
            nested tibbles

        """
        key  = kwargs.get("key", 'data')
        data = kwargs.get("data", [c for c in self.names if c not in by])
        names_sep = kwargs.get("names_sep", None)

        out = (self
               .group_by(by)
               .agg(**{
                   key : pl.struct(data).map_elements(
                       # lambda cols: from_polars( pl.DataFrame(cols.to_list()) ) )
                       lambda cols: from_polars(pl.DataFrame({'data':cols}).unnest('data')) )
                       # lambda cols: tibble(cols.to_list()) )
               })
               .pipe(from_polars)
               )
        # to keep enum order in the nested data
        # enum_columns = [col for col in self.select(data).names
        #                 if self.pull(col).dtype == pl.Enum]
        # if enum_columns:
        #     for col in enum_columns:
        #         cats = self.pull(col).cat.get_categories().to_list()
        #         print(cats)
        #         out = out.mutate(**{key : map([key], lambda row:
        #                                       row[0].mutate(col = as_factor(col, cats) )
        #                                       }
        # # to keep factors
        # factors = [col for col in self.select(data).names
        #                 if self.pull(col).dtype == pl.Categorical]
        # if factors:
        #     for col in factors:
        #         out = out.mutate(**{col : as_factor(col)})


        if names_sep is not None:
            new_names = {col:f"{col}_{names_sep}" for col in data}
            print(new_names)
            out = out.mutate(**{key:col(key).map_elements(lambda row: row.rename(new_names))})
        return out

    def unnest(self, col):
        """
        Unnest a nested tibble
        Parameters
        ----------
        col : str
            Columns to unnest

        Returns
        -------
        tibble
            The nested tibble will be expanded and become unested
            rows of the original tibble.

        """
        assert isinstance(col, str), "'col', must be a string"
        # not run: error if nested df has different columns
        # out = (self
        #        .mutate(**{
        #            col : pl.col(col).map_elements(lambda d: d.to_struct())
        #        })
        #        .to_polars()
        #        .explode(col)
        #        .unnest(col)
        #        )
        # return out.pipe(from_polars)
        out = tibble()
        for row in self.to_polars().iter_rows(named=True):
            n = row[col].nrow
            ids = {c:v for c, v in row.items() if c not in col}
            cols = list(ids.keys())
            df_ids = from_polars(pl.DataFrame(ids)
                                 .with_columns(pl.col(cols) .repeat_by(n))
                                 .explode(cols))
            out = out.bind_rows(df_ids.bind_cols(row[col]))
        out = self.__unnest_cast__(self, out)
        return out

    def __unnest_cast__(self, df_source, df_target):
        # """
        # Align the types of columns in df_target to match categorical and enum columns from df_source,
        # preserving the original column order.

        # Parameters:
        #     df_source: DataFrame containing categorical and enum columns.
        #     df_target: DataFrame whose column types need to be aligned.

        # Returns:
        #     A new DataFrame with types aligned to match df_source for categorical and enum columns,
        #     preserving column order.
        # """
        df_source = df_source.to_polars()
        df_target = df_target.to_polars()
        cat_enum_cols = [
            col for col, dtype in zip(df_source.columns, df_source.dtypes)
            if dtype in [pl.Categorical, pl.Enum]
        ]

        for col in cat_enum_cols:
            if col in df_target.columns:
                if df_source.schema[col] == pl.Categorical:
                    df_target = df_target.with_columns(pl.col(col).cast(pl.Categorical))
                elif isinstance(df_source.schema[col], pl.Enum):
                    enum_dtype = df_source.schema[col]
                    df_target = df_target.with_columns(pl.col(col).cast(enum_dtype))

        return from_polars(df_target.select(df_target.columns))

    def crossing(self, *args, **kwargs):
        """
        Expands the existing tibble for each value of the
        variables used in the `crossing()` argument. See Returns.

        Parameters
        ----------
        *args : list
            One unamed list is accepted. 
        
        *kwargs : list
            keyword will be the variable name, and the values in the list
            will be in the expanded tibble
            
        Returns
        ------- 
        tibble
            A tibble with varibles containing all combinations of the
            values in the arguments passed to `crossing()`. The original
            tibble will be replicated for each unique combination.

        Examples
        -------- 
        >>> df = tp.tibble({'a': [1, 2], "b": [3, 5]})
        >>> df
        shape: (2, 2)
        ┌───────────┐
        │   a     b │
        │ i64   i64 │
        ╞═══════════╡
        │   1     3 │
        │   2     5 │
        └───────────┘
        >>> df.crossing(c = ['a', 'b', 'c'])
        shape: (6, 3)
        ┌─────────────────┐
        │   a     b   c   │
        │ i64   i64   str │
        ╞═════════════════╡
        │   1     3   a   │
        │   1     3   b   │
        │   1     3   c   │
        │   2     5   a   │
        │   2     5   b   │
        │   2     5   c   │
        └─────────────────┘
        """
        out = self.mutate(*args, **kwargs).to_polars()
        for var,_ in kwargs.items():
            out = out.explode(var)
        return out.pipe(from_polars)

    def glimpse(self, regex='.'):
        """
        Print compact information about the data

        Parameters
        ----------
        regex : str, list, dict
            Return information of the variables that match the regular 
            expression, the list, or the dictionary. If dictionary is 
            used, the variable names must be the dictionary keys.

        Returns
        -------
        None

        """
        assert isinstance(regex, str) or\
            isinstance(regex, list) or\
            isinstance(regex, dict), "regex must be a list, dict, or regular expression"
        
        # if isinstance(regex, str):
        #     df = self.select(regex=regex)
        # elif isinstance(regex, dict):
        #     df = self.select(names=list(regex.keys()))
        # else:
        #     df = self.select(names=regex)
        print(f"Columns matching pattern '{regex}':")
        df = self.select(matches(regex)).to_pandas()
        size_col=80
        header_var = 'Var'
        header_type = 'Type'
        header_uniq = 'Uniq'
        header_missing = 'Miss'
        header_missing_perc = '(%)'
        header_head = 'Head'
        # 
        length_col  = np.max([len(header_var)] +
                             [len(col) for col  in df.columns])
        length_type = np.max([len(header_type)] +
                             [len(col) for col  in
                              df.dtypes.astype(str).values]) + 2
        length_nvalues = np.max([len(header_uniq),
                                 len(str(np.max(df
                                                .apply(pd.unique)
                                                .apply(len))))])
        length_missing = np.max([len(header_missing)] +
                                df.isna().sum().astype(str).apply(len).tolist())
        try:
            length_missing_perc = np.max([len(header_missing_perc), 
                                            len((100*df.isna().sum()/df.shape[0])
                                                .max().astype(int)
                                                .astype(str))+2]
                                           )
        except:
            length_missing_perc = 3

        length_head = size_col - (length_col + length_type + length_nvalues + length_missing )
        # 
        header = (f"{header_var:>{length_col}s} "+
                  f"{header_type:{length_type}s}"+
                  f"{header_uniq:>{length_nvalues}s} "+
                  f"{header_missing:>{length_missing}s} "+
                  f"{header_missing_perc:>{length_missing_perc}s} "+
                  f"{header_head:{length_head}s}")
        print(header)
        hline = "-"*size_col
        # print(hline)
        for col in df.columns:
            dtype = str(df[col].dtype)
            nvalues = len(df[col].unique())
            missings = df[col].isna().sum()
            missings_perc = str(int(100*missings/self.nrow))+"%"
            # 
            vals = str(df[col].values)
            vals = vals[:length_head] + (vals[length_head+1:], '...')[len(vals) > length_head]
            # 
            print(f"{col:>{length_col}.{length_col}s} "+
                  f"{'<'+dtype+'>':{length_type}.{length_type}s}"+
                  f"{nvalues:>{length_nvalues}d} "+
                  f"{missings:>{length_missing}d}"+
                  f"{missings_perc:>{length_missing_perc}s} "
                  f"{vals:.{length_head+3}s}")
        # print(hline)
        # print(header)
        print('')
        print(f"[Rows: {self.nrow}; Columns {self.ncol}]")
        return None

    # Not tidy functions, but useful from pandas/polars 
    # -------------------------------------------------
    def replace(self, rep, regex=False):
        """
        Replace method from polars pandas. Replaces values of a column.

        Parameters
        ----------
        rep : dict
            Format to use polars' replace:
                {<varname>:{<old value>:<new value>, ...}}
            Format to use pandas' replace:
                {<old value>:<new value>, ...}

        regex : bool
            If true, replace using regular expression. It uses pandas
            replace()

        Returns
        -------
        tibble
            Original tibble with values of columns replaced based on
            rep`.
        """
        if regex or not all(isinstance(value, dict) for value in rep.values()):
            engine = 'pandas'
        else:
            engine = 'polars'
            
        if engine=='polars':
            out = self.to_polars()
            for var, rep in rep.items():
                try:
                    out = out.with_columns(**{var : pl.col(var).replace(rep)})
                except :
                    out = out.with_columns(**{var : pl.col(var).replace_strict(rep)})
            out = out.pipe(from_polars)
        else:
            out = self.to_pandas()
            out = out.replace(to_replace=rep, regex=regex)
            out = out.pipe(from_pandas)
                    
        return out
        
    def print(self, n=1000, ncols=1000, str_length=1000, digits=2):
        """
        Print the DataFrame

        Parameters
        ----------
        n : int, default=1000
            Number of rows to print

        ncols : int, default=1000
            Number of columns to print

        str_length : int, default=1000
            Maximum length of the strings.

        Returns
        -------
        None
        """
        with pl.Config(set_tbl_rows=n,
                       set_tbl_cols=ncols,
                       float_precision=digits,
                       fmt_str_lengths=str_length):
            print(self)

    def iterrows(self):
        yield from self.to_polars().iter_rows(named=True)
        

    # Statistics 
    # ----------
    def descriptive_statistics(self, vars=None, groups=None,
                               include_categorical=True,
                               include_type=False):
        """
        Compute descriptive statistics for numerical variables and optionally
        frequency statistics for categorical variables, with support for grouping.

        Parameters
        ----------
        vars : str, list, dict, or None, default None
            The variables for which to compute statistics.
            - If None, all variables in the dataset (as given by `self.names`) are used.
            - If a string, it is interpreted as a single variable name.
            - If a list, each element is treated as a variable name.
            - If a dict, keys are variable names and values are their labels.
        groups : str, list, dict, or None, default None
            Variable(s) to group by when computing statistics.
            - If None, overall statistics are computed.
            - If a string, it is interpreted as a single grouping variable.
            - If a list, each element is treated as a grouping variable.
            - If a dict, keys are grouping variable names and values are their labels.
        include_categorical : bool, default True
            Whether to include frequency statistics for categorical variables in the output.
        include_type : bool, default False
            If True, adds a column indicating the variable type ("Num" for numerical, "Cat" for categorical).

        Returns
        -------
        tibble
            A tibble containing the descriptive statistics.
            For numerical variables, the statistics include:
                - N: count of non-missing values
                - Missing (%): percentage of missing values
                - Mean: average value
                - Std.Dev.: standard deviation
                - Min: minimum value
                - Max: maximum value
            If grouping is specified, these statistics are computed for each group.
            When `include_categorical` is True, frequency statistics for categorical variables are appended
            to the result.
        """
        assert isinstance(vars, str) or isinstance(vars, list) or \
            isinstance(vars, dict) or vars is None, \
            "'vars' must be a string, dict, or list"
        assert isinstance(groups, str) or isinstance(groups, list) or \
            isinstance(groups, dict) or groups is None, \
            "'groups' must be a string, dict, or list"

        if vars is None:
            vars = {v:v for v in self.names}
        elif isinstance(vars, str):
            vars = {vars:vars}
        elif isinstance(vars, list):
            vars = {v:v for v in vars}

        if isinstance(groups, str):
            groups = {groups:groups}
        elif isinstance(groups, list):
            groups = {g:g for g in groups}
        
        if isinstance(groups, dict):
            for g in groups.keys():
                vars.pop(g, None)

        # select only numerical
        vars_num = {var:label for var, label in vars.items() if
                    self.to_polars().schema[var].is_numeric()}
        # select only numerical
        vars_cat = {var:label for var, label in vars.items() if
                    not self.to_polars().schema[var].is_numeric()}

        # compute statistics for numerical variables
        if groups is None:
            res = self.__descriptive_statistics__(self, vars_num)
        else:
            res = (self
                   .select(vars_num | groups)
                   .nest(list(groups.values()))
                   .mutate(summary = map(['data'], lambda col:
                                         self.__descriptive_statistics__(col[0],
                                                                         vars=vars_num)))
                   .drop('data')
                   .unnest('summary')
                   )

        n = self.nrow
        res = (res
               .mutate(null_count = 100*pl.col("null_count")/n,
                       count = as_integer('count'))
               .rename({"count":'N',
                        'null_count':'Missing (%)',
                        "mean":"Mean",
                        'std':'Std.Dev.',
                        'min':"Min",
                        'max':'Max'
                        })
               )
        if include_type:
            res = res.mutate(Type='Num')

        # compute statistics for categorical variables
        if vars_cat and include_categorical: 
            res_cat = tibble()
            for var_cat, label in vars_cat.items():
                res_cat = res_cat.bind_rows(
                    self
                    .freq({var_cat:label}, groups=groups)
                    .drop('low', 'high')
                    .rename({'Freq':"Mean",
                             label:'Variable'})
                    .mutate(Variable = label + " ("+pl.col("Variable")+")")
                    .replace_null({'Variable': label + " (Missing)"})
                )
            if include_type:
                    res_cat = res_cat.mutate(Type='Cat')
            res = res.bind_rows(res_cat)

        res = res.arrange('Variable')
        return res

    def __descriptive_statistics__(self, data, vars=None):
            res = (data
                   .select(vars)
                   .to_polars()
                   .describe()
                   .pipe(from_polars)
                   .pivot_longer(cols=list(vars.values()), names_to='Variable', values_to='value')
                   .pivot_wider(names_from='statistic', values_from='value')
                   )
            return res

    def freq(self, vars=None, groups=None, na_rm=False, na_label=None):
        """
        Compute frequency table.

        Parameters
        ----------
        vars : str, list, or dict
            Variables to return value frequencies for. 
            If a dict is provided, the key should be the variable name
            and the values the variable label for the output

        groups : str, list, dict, or None, optional
            Variable names to condition marginal frequencies on. 
            If a dict is provided, the key should be the variable name
            and the values the variable label for the output
            Defaults to None (no grouping).

        na_rm : bool, optional
            Whether to include NAs in the calculation. Defaults to False.

        na_label : str
            Label to use for the NA values
        
        Returns
        -------
        tibble
            A tibble with relative frequencies and counts.
        """
        assert vars, "Parameter 'vars' not informed."
        assert isinstance(groups, str) or \
            isinstance(groups, list) or\
            isinstance(groups, dict) or\
            groups is None, "Incorrect 'groups' argument format. See documentation."
            
        vars_all = []

        if groups is None:
            groups = {}
        elif isinstance(groups, str):
            groups = {groups:groups}
        elif isinstance(groups, list):
            groups = {g:g for g in groups}
        vars_all += list(groups.keys())

        if vars is None:
            vars = {v:v for v in self.names}
        elif isinstance(vars, str):
            vars = {vars:vars}
        elif isinstance(vars, list):
            vars = {v:v for v in vars}
        vars_all += list(vars.keys())

        # labels = False
        # if isinstance(vars, str):
        #     vars = [vars]
        # elif isinstance(vars, dict):
        #     labels = True
        #     vars_labels = vars
        #     vars = list(vars.keys())
        # elif type(vars) is {}.keys().__class__:
        #     vars = list(vars)

        # if groups and not isinstance(groups, list):
        #     groups = [groups]
        # if groups:
        #     vars = groups + vars

        res=self.select(vars_all)
        
        if not na_rm:
            if na_label is not None:
                res=res.replace_null({var:na_label for var in vars})
        else:
            res=res.drop_null()
    
        if not groups:
            res=(res
                   .group_by(vars_all)
                 .summarize(n = n())
                 .mutate(
                       p     = pl.col("n")/pl.col("n").sum(),
                       freq  = 100*pl.col("p"),
                       stdev = 100*np.sqrt((pl.col('p')*(1-pl.col('p')))/pl.col('n'))
                 )
            )
            # for var in vars:
            #     res = self.__tab_reorder_na__(res, var, na_label)
        else:
            res = (res
                   .group_by(vars_all)
                   .summarize(n = n())
                   .group_by(list(groups.keys()))
                   .mutate(
                       p     = pl.col("n")/pl.col("n").sum(),
                       freq  = 100*pl.col("p"),
                       stdev = 100*np.sqrt((pl.col('p')*(1-pl.col('p')))/pl.col('n'))
                   )
            )

        # vars.reverse()
        res = (
            res
            .drop('p')
            .mutate(n = as_integer('n'),
                    low  = pl.col('freq')-1.96*pl.col('stdev'),
                    high = pl.col('freq')+1.96*pl.col('stdev'))
            .rename({'n':'N',
                     'stdev':'Std.Dev.',
                     'freq':'Freq'}, tolower=False)
            .arrange(list(vars.keys()))
        )

        res = res.rename(vars | groups)
        return res

    def tab(self, row, col, groups=None,
            margins=True, normalize='all',#row/columns
            margins_name='Total', stat='both',
            na_rm=True, na_label='NA', digits=2):
        """
        Create a 2x2 contingency table for two categorical variables, with optional grouping,
        margins, and normalization.

        Parameters
        ----------
        row : str
            Name of the variable to be used for the rows of the table.
        col : str
            Name of the variable to be used for the columns of the table.
        groups : str or list of str, optional
            Variable name(s) to use as grouping variables. When provided, a separate 2x2 table
            is generated for each group.
        margins : bool, default True
            If True, include row and column totals (margins) in the table.
        normalize : {'all', 'row', 'columns'}, default 'all'
            Specifies how to compute the marginal percentages in each cell:
              - 'all': percentages computed over the entire table.
              - 'row': percentages computed across each row.
              - 'columns': percentages computed down each column.
        margins_name : str, default 'Total'
            Name to assign to the row and column totals.
        stat : {'both', 'perc', 'n'}, default 'both'
            Determines the statistic to display in each cell:
              - 'both': returns both percentages and sample size.
              - 'perc': returns percentages only.
              - 'n': returns sample size only.
        na_rm : bool, default True
            If True, remove rows with missing values in the `row` or `col` variables.
        na_label : str, default 'NA'
            Label to use for missing values when `na_rm` is False.
        digits : int, default 2
            Number of digits to round the percentages to.

        Returns
        -------
        tibble
            A contingency table as a tibble. The table contains counts and/or percentages as specified
            by the `stat` parameter, includes margins if requested, and is formatted with group headers
            when grouping variables are provided.
        """
        tab = self.select(row, col, groups).mutate(**{row:as_character(row),
                                                      col:as_character(col)})
        vars_row = row
        vars_col = col
        if na_rm:
            tab = tab.drop_null()
        else:
            repl = {var:na_label for var in [row, col]}
            tab = tab.replace_null(repl)
        tab = tab.to_pandas()
        if groups:
            groups = [groups] if isinstance(groups, str) else groups
            ngroups=len(groups)
            resn = self.__tab_groups__(tab, vars_row, vars_col, normalize=False,
                                       margins=margins, margins_name=margins_name,
                                       groups=groups)
            resp = self.__tab_groups__(tab, vars_row, vars_col, normalize,
                                       margins, margins_name, groups)
        else:
            ngroups=0
            resn = self.__tab__(tab, vars_row, vars_col, normalize=False,
                                margins=margins, margins_name=margins_name)
            resp = self.__tab__(tab, vars_row, vars_col, normalize=normalize,
                                margins=margins, margins_name=margins_name)
        colsn=resn.columns[ngroups+1:]
        colsp=resp.columns[ngroups+1:]
        res=resp.iloc[:,0:ngroups+1]

        if stat=='both':
            for coln, colp in zip(colsn, colsp):
                col = [f"{round(100*p, digits)} % ({n})" for p,n
                       in zip(resp[colp], resn[coln])]
                res = res.assign(**{coln:col})
        elif stat=='perc':
            for colp in colsp:
                res = res.assign(**{str(colp):100*resp[colp]})
        else:
            for coln in colsn:
                res = res.assign(**{str(coln):100*resp[coln]})
        # Group columns using varname as label
        ncat = len(tab[vars_col].unique())
        ngroups = 0 if not groups else len(groups)
        col_groups = ['']*(ngroups+1) + [vars_col]*ncat+['']
        col_ix = pd.MultiIndex.from_arrays([col_groups, res.columns])
        res.columns = col_ix
        res.columns.names = ['', '']
        res.columns.name = ''
        res.columns = [col[1] for col in res.columns]
        res = self.__tab_reorder_na__(res, row, na_label)
        return from_pandas(res)

    def __tab__(self, tab, row, col, normalize='all', margins=True, margins_name='Total'):
        if normalize=='row':
            normalize='index'
        if normalize=='column' or normalize=='col':
            normalize='columns'
        res = pd.crosstab(index=[tab[row]],
                          columns=[tab[col]],
                          margins=margins, margins_name=margins_name,
                          normalize=normalize)
        res = res.reset_index(drop=False)
        return res

    def __tab_groups__(self, tab, vars_row, vars_col, normalize,
                       margins, margins_name, groups):
        res = (tab
               .groupby(groups)
               .apply(self.__tab__,
                      vars_row, vars_col, normalize, margins, margins_name)
               .reset_index(drop=False)
        )
        cols = [col for cidx, col in enumerate(list(res.columns) ) if
                not bool(re.search(pattern='^level_[0-9]$', string=col))]
        res=res.filter(cols)
        return res

    def __tab_reorder_na__(self, tab, row, na_label):
        tab = from_pandas(tab).to_polars()
        # Check if "Total" column exists and place "AB" before it
        if na_label in tab.columns:
            if "Total" in tab.columns:
                total_index = tab.columns.index("Total")
                columns = tab.columns[:total_index] + [na_label] + tab.columns[total_index:]
                if na_label in tab.columns:
                    columns.remove(na_label)  # Avoid duplication of "AB"
                tab = tab.select(columns)
          
        # Check if "Total" row exists and move "ABC" before it
        if na_label in tab[row]:
            na_row = tab.filter(tab[row] == na_label)
            non_na_rows = tab.filter(tab[row] != na_label)
            if "Total" in tab[row].to_list():
                total_row_index = non_na_rows[row].to_list().index("Total")
                before_total_rows = non_na_rows[:total_row_index]
                after_total_rows = non_na_rows[total_row_index:]
                tab = pl.concat([before_total_rows, na_row, after_total_rows], how="vertical")
          
            else:
                tab = pl.concat([non_na_rows, na_row], how="vertical")
        return tab.to_pandas()

    # Reporting 
    # ---------
    def to_latex(self,
                 header = None,
                 digits = 4,
                 caption = None,
                 label = None,
                 align = None,
                 na_rep  =  '',
                 position = '!htb',
                 group_rows_by = None,
                 group_title_align = 'l',
                 footnotes = None,
                 index = False,
                 escape = False,
                 longtable = False,
                 longtable_singlespace = True,
                 rotate = False,
                 scale = True,
                 parse_linebreaks=True,
                 tabular = False
                 ):
        """
        Convert the object to a LaTeX tabular representation.

        Parameters
        ----------
        header : list of tuples, optional
            The column headers for the LaTeX table. Each tuple corresponds to a column.
            Ex: This will create upper level header with grouped columns
                [("", "col 1"),
                 ("Group A", "col 2"),
                 ("Group A", "col 3"),
                 ("Group B", "col 4")
                 ("Group B", "col 5"),
                  ]
                This will create two upper level header with grouped columns
                [("Group 1", ""       , "col 1"),
                 ("Group 1", "Group A", "col 2"),
                 ("Group 1", "Group A", "col 3"),
                 (""       , "Group B", "col 4")
                 (""       , "Group B", "col 5"),
                  ]
        digits : int, default=4
            Number of decimal places to round the numerical values in the table.

        caption : str, optional
            The caption for the LaTeX table.

        label : str, optional
            The label for referencing the table in LaTeX.

        align : str, optional
            Column alignment specifications (e.g., 'lcr').

        na_rep : str, default=''
            The representation for NaN values in the table.

        position : str, default='!htbp'
            The placement option for the table in the LaTeX document.

        footnotes : dict, optional
            A dictionary where keys are column alignments ('c', 'r', or 'l')
            and values are the respective footnote strings.

        group_rows_by : str, default=None
            Name of the variable in the data with values to group
            the rows by.

        group_title_align str, default='l'
            Alignment of the title of each row group

        index : bool, default=False
            Whether to include the index in the LaTeX table.

        escape : bool, default=False
            Whether to escape LaTeX special characters.

        longtable : bool, deafult=False
            If True, table spans multiple pages

        longtable_singlespace : bool
            Force single space to longtables

        rotate : bool
            Whether to use landscape table

        scale : bool, default=True
            If True, scales the table to fit the linewidth when
            the table exceeds that size
            Note: ignored when longtable=True. This is a LaTeX
                  limitation because longtable does not use
                  tabular.

        parse_linebreaks : book, default=True
            If True, parse \\n and replace it with \\makecel
            to produce linebreaks

        tabular : bool, default=False
            Whether to use a tabular format for the output.

        Returns
        -------
            str
                A LaTeX formatted string of the tibble.
        """

        assert footnotes is None or isinstance(footnotes, dict),\
            "'footnote' must be a dictionary"

        # this must be the first operation
        if group_rows_by is not None:
            self = self.arrange(group_rows_by)
            tabm = self.to_pandas().drop([group_rows_by], axis=1)
        else:
            tabm = self.to_pandas()
        ncols = tabm.shape[1]

        if tabular and not longtable:
            position=None

        if align is None:
            align = 'l'*ncols

        if header is not None:
            tabm.columns = pd.MultiIndex.from_tuples(header)
            
        tabl = (tabm
                # .round(digits)
                # .astype(str)
                .to_latex(index = index,
                          escape = escape,
                          caption = caption,
                          label = label,
                          sparsify = True,
                          multirow = True,
                          multicolumn = True,
                          multicolumn_format = 'c',
                          column_format = align,
                          bold_rows = True,
                          na_rep = na_rep,
                          float_format=f"%.{digits}f",
                          position = position
                          ))

        # split to add elements
        rows = tabl.splitlines()

        if group_rows_by is not None:
            rows = self.__to_latex_group_rows__(group_rows_by, group_title_align, ncols, rows)

        # add centering
        row = [i for i, txt in enumerate(rows) if
               bool(re.search(pattern='begin.*tabular', string=txt))][0]
        rows.insert(row,f"\\centering")

        footnotes_formated = ""
        if footnotes is not None:
            for align_note, footnote in footnotes.items():
                footnote = [footnote] if isinstance(footnote, str) else footnote
                for fni in footnote:
                    notes = f"\\multicolumn{{{ncols}}}{{{align_note}}}{{{fni}}}\\\\"
                    footnotes_formated += notes
                    if not longtable:
                        row = [idx for idx, s in enumerate(rows) if 'bottomrule' in s ][0]
                        rows.insert(row + 1, notes)


        # rejoin table
        tabl = "\n".join(rows)

        # add midrules
        if header is not None:
            tabl = self.__to_latex_add_midrules_to_table__(tabl)

        if longtable:
            tabl = self.__to_latex_multipage__(tabl, caption, ncols, align,
                                               label, position,
                                               footnotes_formated,
                                               longtable_singlespace)

        if rotate:
            tabl = re.sub(pattern="^", repl='\\\\begin{landscape}', string=tabl)
            tabl = re.sub(pattern="$", repl='\\\\end{landscape}', string=tabl)

        if scale and not longtable:
            box = '\\resizebox{\\ifdim\\width>\\linewidth\\linewidth\\else\\width\\fi}{!}{'
            tabl = tabl.replace('\\begin{tabular}', f"{box}\n\\begin{{tabular}}")
            tabl = tabl.replace('\\end{tabular}', "\\end{tabular}}")

        # linebreaks:
        if parse_linebreaks:
            tabl = self.__to_latex_breaklines__(tabl)    

        return tabl

    def __to_latex_process_header_line_for_cmid__(self, line: str) -> str:
        # Given a header line (without the trailing newline),
        # parse for multicolumn commands and generate a line of cmidrule(s)
        # based on the non-empty group labels.

        # Example:
        #   Input line: r"\\multicolumn{3}{c}{Combine} & \\multicolumn{3}{c}{} \\"
        #   Output: r"\\cmidrule(lr){1-3} \\"

        # Remove trailing "\\" if present
        line_clean = line.strip()
        if line_clean.endswith(r'\\'):
            line_clean = line_clean[:-2].strip()

        # Split the row into cells (assuming & is the column separator)
        cells = [cell.strip() for cell in line_clean.split('&')]
        col_counter = 0
        midrules = []

        # Regex to capture multicolumn: number of columns and content.
        # This assumes a simple structure without nested braces.
        multicolumn_pattern = re.compile(r'\\multicolumn\{(\d+)\}\{[^}]*\}\{([^}]*)\}')

        for cell in cells:
            m = multicolumn_pattern.search(cell)
            if m:
                span = int(m.group(1))
                content = m.group(2).strip()
                start = col_counter + 1
                end = col_counter + span
                # Only add a midrule if the cell’s content is not empty
                if content:
                    midrules.append(r'\cmidrule(lr){' + f"{start}-{end}" + '}')
                col_counter += span
            else:
                # A normal cell occupies one column.
                col_counter += 1

        if midrules:
            # Join the midrule commands (separated by a space) and add the trailing \\.
            return " ".join(midrules) #+ r' \\'
        else:
            return ""

    def __to_latex_add_midrules_to_table__(self, latex_table: str) -> str:
        # Given a LaTeX table (as a string) that uses booktabs commands,
        # insert automatically generated cmidrule lines for header rows that
        # contain multicolumn cells.

        # Assumes that the header is contained between the \\toprule and the first \\midrule.
        lines = latex_table.splitlines()
        new_lines = []
        in_header = False
        header_lines = []  # temporarily hold header lines

        for line in lines:
            # When we hit \toprule, we start the header section.
            if r'\toprule' in line:
                in_header = True
                new_lines.append(line)
            # When we hit the first \midrule, process any stored header rows.
            elif in_header and r'\midrule' in line:
                # Process each header line: output the line and, if applicable, a cmidrule line.
                for hline in header_lines:
                    new_lines.append(hline)
                    cmid_line = self.__to_latex_process_header_line_for_cmid__(hline)
                    if cmid_line:
                        new_lines.append(cmid_line)
                # Now add the \midrule line and stop header processing.
                new_lines.append(line)
                in_header = False
                header_lines = []
            elif in_header:
                # Collect header rows (these are the lines between \toprule and \midrule).
                header_lines.append(line)
            else:
                # Outside the header section, just pass the line along.
                new_lines.append(line)

        return "\n".join(new_lines)

    def __to_latex_multipage__(self, tabl, caption, ncols, align,
                               label, position, footnote,
                               longtable_singlespace):
        header_old = self.__to_latex_extract_header__(tabl)
        header_new = f"""
          {header_old}

        \\endfirsthead
          \\caption[]{{ {caption} }}\\\\

         \\multicolumn{{{ncols}}}{{l}}{{\\textit{{(continued)}}}}\\\\
        \\toprule
          {header_old}
        \\midrule
        \\endhead

        \\bottomrule
        {footnote}
        \\multicolumn{{{ncols}}}{{r@{{}}}}{{\\textit{{(continued \\ldots)}}}}\\\\
        \\endfoot
        {footnote}
        \\endlastfoot
        """

        longtable_begin = f'\\begin{{longtable}}{{{align}}}'
        longtable_end   = f'\\end{{longtable}}'
        if longtable_singlespace:
            longtable_begin = '\\begin{spacing}{1}\n' + longtable_begin 
            longtable_end   =  longtable_end + "\n\\end{spacing}"
        
        tabl = (tabl
                .replace(f"\\begin{{table}}[{position}]", longtable_begin)
                .replace("\\end{table}", longtable_end)

                .replace(f"\\label{{{label}}}", f"\\label{{{label}}}\\\\")

                .replace("\\centering", '')
                .replace(f"\\begin{{tabular}}{{{align}}}", '')
                .replace("\\end{tabular}", '')
                
                .replace(header_old, header_new)
                )
        return tabl
    
    def __to_latex_extract_header__(self, latex_table: str) -> str:
        # Extract the header section from a LaTeX table.

        # The header is defined as the text between the first occurrence of
        # '\\toprule' and '\\midrule'. This function returns that section
        # as a single string.

        # Parameters:
        #   latex_table (str): The complete LaTeX table as a string.

        # Returns:
        #   str: The header lines between '\\toprule' and '\\midrule', with
        #        surrounding whitespace removed.

        # Use re.DOTALL so that '.' matches newline characters.
        pattern = re.compile(r'\\toprule\s*(.*?)\s*\\midrule', re.DOTALL)
        match = pattern.search(latex_table)
        if match:
            return match.group(1).strip()
        else:
            return ""

    def __to_latex_group_rows__(self, group_rows_by, group_title_align, ncols, rows):

        position_first_row = self.__to_latex_group_rows_starting_positions__(rows)
        position_last_row = self.__to_latex_group_rows_ending_positions__(rows, position_first_row)

        # get groups locations
        groups = (self
                  .pull(group_rows_by)
                  .to_list())
        groups_row_locations = {groups[0]: 0}
        for i in range(1, len(groups)):
            if groups[i] != groups[i-1]:
                groups_row_locations[groups[i]] = i

        # insert horizontal space on grouped rows
        for i in range(position_first_row, position_last_row):
            rows[i] = '\\hspace{1em}' + rows[i] 

        # insert groups heading rows
        for key, pos in sorted(groups_row_locations.items(),
                               key=lambda item: item[1], reverse=True):
            group_title = f"\\addlinespace[0.3em]\\multicolumn{{{ncols}}}{{{group_title_align}}}{{ \\textbf{{{key}}} }}\\\\"
            rows.insert(position_first_row + pos, group_title )

        return rows

    def __to_latex_group_rows_starting_positions__(self, rows):
        # Given a list of LaTeX table rows, returns the index of the first row
        # containing '\\midrule' after the last occurrence of a row containing '\\toprule'.
        # If either token is not found, the function returns None.

        last_top_index = -1
        res = None

        # Iterate over rows to find the last index containing '\toprule'
        for i, row in enumerate(rows):
            if r'\toprule' in row:
                last_top_index = i

        if last_top_index == -1:
            res = None

        # Search for the first occurrence of '\midrule' after the last '\toprule'
        for i in range(last_top_index + 1, len(rows)):
            if r'\midrule' in rows[i]:
                res = i+1  # Return the index of the row containing '\midrule'

        return res

    def __to_latex_group_rows_ending_positions__(self, rows, position_first_row):
        last_table_row_index = -1
        for i, row in enumerate(rows[position_first_row:]):
            if r'\bottomrule' in row:
                last_table_row_index = position_first_row + i
                break

        return last_table_row_index 

    def __to_latex_breaklines__(self, table_str):
        # Given a LaTeX table string containing a tabular environment,
        # replace internal newline characters within table cells (i.e. those
        # that occur within the cell content, not the row terminators) by 
        # LaTeX line breaks and wrap the cell text with \makecell{...}.

        # Table rules such as \\toprule, \midrule, and \\bottomrule are left untouched.

        # Parameters:
        #     table_str (str): A string containing a LaTeX table.

        # Returns:
        #     str: The modified LaTeX table string.

        def process_tabular(match):
            # match.group(1): The \begin{tabular}{...} line
            # match.group(2): The content inside the tabular environment
            # match.group(3): The \end{tabular} line
            begin_tabular = match.group(1)
            content = match.group(2)
            end_tabular = match.group(3)

            # Split the content into parts while preserving the row separator.
            # We assume each row ends with a double backslash (\\) followed by optional whitespace and a newline.
            parts = re.split(r'(\\\\\s*\n|\\toprule\n|\\midrule\n|\\bottomrule\n)', content)

            # Reassemble rows as tuples: (row_text, row_separator)
            rows = []
            for i in range(0, len(parts), 2):
                row_text = parts[i]
                separator = parts[i+1] if i+1 < len(parts) else ''
                rows.append((row_text, separator))

            processed_rows = []
            for row_text, row_sep in rows:
                # Skip processing for rows that are table rules.
                if row_text.strip() in ('\\toprule', '\\midrule', '\\bottomrule') or\
                   bool(re.search(pattern="cmidrule", string=row_text)):
                    processed_rows.append(row_text + row_sep)
                    continue

                # Split the row into cells using the ampersand (&) as the delimiter.
                cells = row_text.split('&')
                new_cells = []
                for cell in cells:
                    # Remove only trailing whitespace from the cell.
                    cell_clean = cell.rstrip()
                    # Check if the cell contains an internal newline.
                    if '\n' in cell_clean:
                        # Remove any extra whitespace from the beginning and end.
                        cell_core = cell_clean.strip()
                        # Split the cell content by newline, strip each line, and join with LaTeX's line-break command.
                        cell_lines = cell_core.split('\n')
                        cell_with_breaks = r'\\'.join(line.strip() for line in cell_lines)
                        # Wrap the content with \makecell{...}
                        cell_processed = r'\makecell{' + cell_with_breaks + '}'
                    else:
                        cell_processed = cell
                    new_cells.append(cell_processed)
                # Reassemble the row from its cells and append the preserved row separator.
                new_row = " & ".join(new_cells)
                processed_rows.append(new_row + row_sep)

            # Reassemble the entire tabular content.
            new_content = "".join(processed_rows)
            return begin_tabular + new_content + end_tabular

        # Process only the tabular environment in the table string.
        new_table_str = re.sub(
            r'(\\begin\{tabular\}\{[^}]*\})(.*?)(\\end\{tabular\})',
            process_tabular,
            table_str,
            flags=re.DOTALL
        )
        return new_table_str

    # Exporting table 
    # ---------------
    def to_excel(self, *args, **kws):
        """
        Save table to excel.

        Details
        -------
        See polars `write_excel()` for details.
        
        Returns
        -------
        None
        """

        self.to_polars().write_excel(*args, **kws)

    def to_csv(self, *args, **kws):
        """
        Save table to csv.

        Details
        -------
        See polars `write_csv()` for details.
        
        Returns
        -------
        None
        """
        self.to_polars().write_csv(*args, **kws)

    def colnames(self, regex='.', type=None, include_factor=True):
        """
        Return the names of numeric columns in `self` that match 'regex'
        type: (str)
            
        include_factor: (boolean)
            When type=string, include or not factors
        
        """
        cols = self.select(matches(regex)).names

        if type:
            if type=='numeric':
                selector = pl.selectors.numeric()
            if type=='integer':
                selector = pl.selectors.integer()
            if type=='string':
                if include_factor:
                    selector = pl.selectors.string() | pl.selectors.categorical() | pl.selectors.enum()
                else:
                    selector = pl.selectors.string()
            if type=='factor':
                selector = pl.selectors.categorical() | pl.selectors.enum()
            if type=='date':
                selector = pl.selectors.date()
            cols_type = self.to_polars().select(selector).columns

            cols = [c for c in cols_type  if c in cols]

        return cols

class TibbleGroupBy(pl.dataframe.group_by.GroupBy):

    def __init__(self, df, by, *args, **kwargs):
        assert isinstance(by, str) or isinstance(by, list), "Use list or string to group by."
        super().__init__(df, by, *args, **kwargs)
        self.df = df
        self.by = by if isinstance(by, list) else [by]

    @property
    def _constructor(self):
        return TibbleGroupBy

    def mutate(self, *args, **kwargs):
        out = self.map_groups(lambda x: from_polars(x).mutate(*args, **kwargs))
        return out

    def filter(self, *args, **kwargs):
        out = self.map_groups(lambda x: from_polars(x).filter(*args, **kwargs))
        return out

    def summarize(self, *args, **kwargs):
        out = self.map_groups(lambda x: from_polars(x).summarise(by=self.by, *args, **kwargs))
        return out

def from_polars(df):
    """
    Convert from polars DataFrame to tibble

    Parameters
    ----------
    df : DataFrame
        pl.DataFrame to convert to a tibble

    Returns
    -------
    tibble

    Examples
    --------
    >>> tp.from_polars(df)
    """
    # df = copy.copy(df)
    # df.__class__ = tibble
    df = tibble(df)
    return df

def from_pandas(df):
    """
    Convert from pandas DataFrame to tibble

    Parameters
    ----------
    df : DataFrame
        pd.DataFrame to convert to a tibble

    Returns
    -------
    tibble

    Examples
    --------
    >>> tp.from_pandas(df)
    """
    if isinstance(df, pd.DataFrame):
        try:
            # Try to convert directly
            df = from_polars(pl.from_pandas(df))
        except Exception as e:
            print(f"Error during conversion: {e}")
            print("Identifying problematic columns...")

            # Identify problematic columns by attempting individual conversions
            problematic_columns = []
            for column in df.columns:
                try:
                    pl.from_pandas(df[[column]])
                except Exception as col_error:
                    print(f"Column '{column}' caused an error: {col_error}")
                    problematic_columns.append(column)

            # Convert problematic columns to string type
            for column in problematic_columns:
                df[column] = df[column].astype(str)
    elif isinstance(df, tibble):
        pass
    elif isinstance(df, pl.DataFrame):
        df = from_polars(df)
    else:
        df = None
    return df
    
_allowed_methods = [
    'dtypes', 'frame_equal',
    'get_columns', 'lazy', 'pipe',
    'iter_rows'
    ]

_polars_methods = [
    'apply',
    'columns',
    'describe',
    'downsample',
    'drop_duplicates',
    'explode',
    'fill_nan',
    'fill_null',
    'find_idx_by_name',
    'fold',
    'get_column',
    'groupby',
    'hash_rows',
    'height',
    'hstack',
    'insert_at_idx',
    'interpolate',
    'is_duplicated',
    'is_unique',
    'join',
    'limit',
    'max',
    'mean',
    'median',
    'melt',
    'min',
    'n_chunks',
    'null_count',
    'quantile',
    'rechunk',
    # 'replace',
    'replace_at_idx',
    'row',
    'rows'
    'sample',
    'select_at_idx',
    'shape',
    'shift',
    'shift_and_fill',
    'shrink_to_fit',
    'sort',
    'std',
    'sum',
    # 'to_arrow',
    # 'to_dict',
    'to_dicts',
    'to_dummies',
    'to_ipc',
    'to_json',
    'to_numpy'
    'to_pandas'
    'to_parquet',
    'transpose',
    # 'unnest',
    'unique',
    'var',
    'width',
    'with_column',
    'with_columns',
    'with_column_renamed',
    'with_columns'
    ]
