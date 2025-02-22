# Basic usage

tidypolars$^{4sci} $ methods are designed to work like tidyverse
functions:

``` {.python exports="both" results="output code" tangle="usage.py" cache="yes" noweb="no" session="*Python-Org*"}
import tidypolars4sci as tp

# create tibble data frame
df = tp.tibble({"x" : range(4),
                "y" : range(3, 7),
                "z" : ['a', 'a', 'b', 'c']})
df = (df
      .select('x', 'y', 'z')
      .filter(tp.col('x') < 4, tp.col('y') > 1)
      .arrange(tp.desc('z'), 'x')
      .mutate(double_x = tp.col('x') * 2,
              x_plus_y = tp.col('x') + tp.col('y'),
              z_num = tp.case_when(tp.col("z")=='a', 1,
                                    tp.col("z")=='b', 2,
                                    True, 0),
              )

      )
df.print()
```

``` python
shape: (4, 6)
┌───────────────────────────────────────────────┐
│   x     y   z     double_x   x_plus_y   z_num │
│ i64   i64   str        i64        i64     i32 │
╞═══════════════════════════════════════════════╡
│   3     6   c            6          9       0 │
│   2     5   b            4          7       2 │
│   0     3   a            0          3       1 │
│   1     4   a            2          5       1 │
└───────────────────────────────────────────────┘
```

# Converting to/from pandas data frames

If you need to use a package that requires pandas or polars data frames,
you can convert from a tidypolars4sci `tibble`{.verbatim} to either of
those `DataFrame`{.verbatim} formats.

``` python
# convert to pandas
df = df.to_pandas()
# or convert to polars
df = df.to_polars()
```

To convert from a pandas or polars `DataFrame`{.verbatim} to a
tidypolars `tibble`{.verbatim}:

``` python
# convert from pandas
df = tp.from_pandas(df)
# or covert from polars
df = tp.from_polars(df)
```
