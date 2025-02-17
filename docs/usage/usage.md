
# Basic usage

tidypolars4sci methods are designed to work like tidyverse functions:

```python
import tidypolars4sci as tp

# create tibble data frame
df = tp.tibble(x = range(3),
               y = range(3, 6),
               z = ['a', 'a', 'b'])

(
    df
    .select('x', 'y', 'z')
    .filter(tp.col('x') < 4, tp.col('y') > 1)
    .arrange(tp.desc('z'), 'x')
    .mutate(double_x = tp.col('x') * 2,
            x_plus_y = tp.col('x') + tp.col('y')
            )
)
┌─────┬─────┬─────┬──────────┬──────────┐
│ x   ┆ y   ┆ z   ┆ double_x ┆ x_plus_y │
│ --- ┆ --- ┆ --- ┆ ---      ┆ ---      │
│ i64 ┆ i64 ┆ str ┆ i64      ┆ i64      │
╞═════╪═════╪═════╪══════════╪══════════╡
│ 2   ┆ 5   ┆ b   ┆ 4        ┆ 7        │
├╌╌╌╌╌┼╌╌╌╌╌┼╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌┤
│ 0   ┆ 3   ┆ a   ┆ 0        ┆ 3        │
├╌╌╌╌╌┼╌╌╌╌╌┼╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌┤
│ 1   ┆ 4   ┆ a   ┆ 2        ┆ 5        │
└─────┴─────┴─────┴──────────┴──────────┘

```

<!-- ## General syntax comparing with tidyverse -->


# Converting to/from pandas data frames
If you need to use a package that requires pandas or polars data frames, you can convert from a tidypolars4sci `tibble` to either of those `DataFrame` formats.

```python
# convert to pandas...
df = df.to_pandas()
# ... or convert to polars
df = df.to_polars()
```

To convert from a pandas or polars `DataFrame` to a tidypolars `tibble`:

```python
# convert from pandas...
df = tp.from_pandas(df)
# or covert from polars
df = tp.from_polars(df)
```
