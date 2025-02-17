![](docs/_css/tidypolars4sci.png)

# TidyPolars $^{4sci}$

**tidypolars4sci** provides functions that match as closely as possible to R's [Tidyverse](https://www.tidyverse.org/) functions for manipulating data frames and conducting data analysis in Python using the blazingly fast [Polars](https://github.com/pola-rs/polars) as backend.

The name **tidypolars4sci** reflects the module's main features:

1. Matches the function names and functionalities of R's [Tidyverse](https://tidyverse.org/).
2. Leverages the performance and efficiency of [Polars](https://github.com/pola-rs/polars) under the hood.
3. Tailored for scientific research, extending the default functionalities of both Polars and Tidyverse.

## Details

**tidypolars4sci** is an **extended** API for [Polars](https://github.com/pola-rs/polars). One of the **main advantages** of using Polars as a data manipulation engine is its exceptional speed when compared to other alternatives (see [here](https://pola.rs/posts/benchmarks/)).

The primary distinction between **tidypolars4sci** and Polars lies in user interaction. The frontend functions are designed to closely resemble those available in R's [Tidyverse](https://tidyverse.org/), making it easier for users familiar with that ecosystem to transition to this library.

Another useful feature of **tidypolars4sci** is its extensive functionality aimed at facilitating data analysis and reporting for scientific research and academic publications. This includes the creation of LaTeX tables, which enhances the presentation of results.

Note: Due to the additional functionalities provided, **tidypolars4sci** may operate slightly slower than using Polars directly.


## Documentation

`<under construction>`


## Installation

You can install tidypolars4sci with `pip`:

```bash
$ pip3 install tidypolars4sci
```

Or through `conda`:
```bash
$ conda install -c conda-forge tidypolars4sci
```

## Basic usage

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


## Converting to/from pandas data frames

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

## Similar projects

- [tidypolars](https://pypi.org/project/tidypolars/): tidypolars was the starting point of tidypolars4sci
