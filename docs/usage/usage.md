# Basic usage

tidypolars$^{4sci} $ methods are designed to work like tidyverse
functions. This creates a dataframe:

``` {.python exports="code" results="none" tangle="src-usage.py" cache="yes" noweb="no" session="*Python*" linenums="1"}
import tidypolars4sci as tp

df = tp.tibble({"x" : range(6),
                "y" : range(6, 12),
                "w" : range(6, 12),
                "z" : ['a', 'a', 'b', 'c', 'd', 'e']}) # (1)!
```

1.  Creates a tibble (the data frame of tidypolars$^{4sci} $)

Here is the dataframe created:

``` python
shape: (6, 4)
┌───────────────────────┐
│   x     y     w   z   │
│ i64   i64   i64   str │
╞═══════════════════════╡
│   0     6     6   a   │
│   1     7     7   a   │
│   2     8     8   b   │
│   3     9     9   c   │
│   4    10    10   d   │
│   5    11    11   e   │
└───────────────────────┘
```

Data manipulation mirrors tidyverse function names:

``` {.python exports="code" results="none" tangle="src-usage.py" cache="yes" noweb="no" session="*Python*" linenums="1"}
df = (df
      .select('x', 'y', 'z') # (1)!
      .filter(tp.col('x') < 4, tp.col('y') >=7) # (2)!
      .arrange(tp.desc('z'), 'x') # (3)!
      .mutate(double_x = tp.col('x') * 2, # (4)!
              x_plus_y = tp.col('x') + tp.col('y'), # (5)!
              z_num = tp.case_when(tp.col("z")=='a', 1, 
                                   tp.col("z")=='b', 2,
                                   True, 0), # (6)!
              )

      )
```

1.  Select columns `x`, `y`, and `z`.
2.  Select (filter) rows with `x < 4` and `y > 7`.
3.  Sort (arrange) the data by `z` (decreasing values) and then by `x`
    (increasing values).
4.  Create a variable `double_x`.
5.  Create a variable `x_plus_y`.
6.  Create a variable `z_num` that is `1` when `z = 'a'`, `2` when
    `z = 'b'`, and `0` otherwise.

``` python
shape: (3, 6)
┌───────────────────────────────────────────────┐
│   x     y   z     double_x   x_plus_y   z_num │
│ i64   i64   str        i64        i64     i32 │
╞═══════════════════════════════════════════════╡
│   3     9   c            6         12       0 │
│   2     8   b            4         10       2 │
│   1     7   a            2          8       1 │
└───────────────────────────────────────────────┘
```

# Converting to/from pandas data frames

If one needs to use a package that requires pandas or polars dataframes,
you can convert from a tidypolars$^{4sci} $ `tibble` to either of those
`DataFrame` formats.

``` {.python exports="code" results="none" tangle="src-usage.py" cache="yes" noweb="no" session="*Python*"}
# convert to pandas
df = df.to_pandas()
# or convert to polars
df = df.to_polars()
```

To convert from a pandas or polars `DataFrame` to a
tidypolars$^{4sci}$\'s `tibble`:

``` {.python exports="code" results="none" tangle="src-usage.py" cache="yes" noweb="no" session="*Python*"}
# convert from pandas
df = tp.from_pandas(df)
# or covert from polars
df = tp.from_polars(df)
```
