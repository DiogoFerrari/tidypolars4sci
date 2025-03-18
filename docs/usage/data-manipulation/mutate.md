## Basic examples

To create new variables based on the transformation of existing ones:

``` {.python exports="code" results="none" tangle="02-mutate.py" cache="yes" noweb="no" session="*Python*" linenums="1"}
import tidypolars4sci as tp
from tidypolars4sci.data import starwars

df = (starwars
      .head(5) # (1)!
      .select('name', 'mass')
      # create two new variables:
      .mutate(mass2 = tp.col('mass') * 2,
              mass2_squared = tp.col('mass2') * tp.col('mass2'),
              )
      )
```

1.  Select the first 5 rows for the example

``` python
shape: (5, 4)
┌──────────────────────────────────────────────────┐
│ name               mass    mass2   mass2_squared │
│ str                 f64      f64             f64 │
╞══════════════════════════════════════════════════╡
│ Luke Skywalker    77.00   154.00       23,716.00 │
│ C-3PO             75.00   150.00       22,500.00 │
│ R2-D2             32.00    64.00        4,096.00 │
│ Darth Vader      136.00   272.00       73,984.00 │
│ Leia Organa       49.00    98.00        9,604.00 │
└──────────────────────────────────────────────────┘
```

## Using default functions

TidyPolars$^{4sci} $ provides many default functions that can be applied
directly to columns. Here is an example:

``` {.python exports="both" results="output code" tangle="src-mutate.py" cache="yes" hlines="yes" colnames="yes" noweb="no" session="*Python*" linenums="1"}
df = (starwars
      .head(5)
      .select('name', 'mass')
      .mutate(mass_avg = tp.col('mass').mean(),
              mass_min = tp.col('mass').min()
              )
      )
df.print()
```

``` python
shape: (5, 4)
┌───────────────────────────────────────────────┐
│ name               mass   mass_avg   mass_min │
│ str                 f64        f64        f64 │
╞═══════════════════════════════════════════════╡
│ Luke Skywalker    77.00      73.80      32.00 │
│ C-3PO             75.00      73.80      32.00 │
│ R2-D2             32.00      73.80      32.00 │
│ Darth Vader      136.00      73.80      32.00 │
│ Leia Organa       49.00      73.80      32.00 │
└───────────────────────────────────────────────┘
```

The module provides many other default functions to apply to columns.
Check the API reference for more. Here are some other examples.

``` {.python exports="both" results="output code" tangle="src-default-functions.py" cache="yes" hlines="yes" colnames="yes" noweb="no" session="*Python*" linenums="1"}
import tidypolars4sci as tp
from tidypolars4sci.data import mtcars as df


(df
 .group_by("am")
 .summarize(disp_avg = tp.col("disp").mean(),
            disp_std = tp.col("disp").std(),
            disp_med = tp.col("disp").median(),
            disp_min = tp.col("disp").min(),
            disp_max = tp.col("disp").max(),
            )
).print()

```

``` python
shape: (2, 6)
┌────────────────────────────────────────────────────────────┐
│  am   disp_avg   disp_std   disp_med   disp_min   disp_max │
│ i64        f64        f64        f64        f64        f64 │
╞════════════════════════════════════════════════════════════╡
│   1     143.53      87.20     120.30      71.10     351.00 │
│   0     290.38     110.17     275.80     120.10     472.00 │
└────────────────────────────────────────────────────────────┘
```

## Using custom functions

The function `map()` allows one to apply user-defined custom functions
in parallel to each row. The result can be stored in a new column of the
data frame using `mutate()`. Here is an example of how to apply custom
functions to one or more columns:

-   Note: the `*` in `*cols` is used to expand the columns. One could
    also use `cols[0], cols[1]` instead.

``` {.python exports="both" results="output code" tangle="src-mutate.py" cache="yes" hlines="yes" colnames="yes" noweb="no" session="*Python*" linenums="1"}
import numpy as np

df = tp.tibble({'a':[1,10,100], 'b':[2, -20, 100]})

def min_of_two(col1, col2):
    return np.min([col1, col2])

df
df = (df
      .mutate(min_ab = tp.map(['a', 'b'], lambda cols: min_of_two(*cols)),
              max_ab = tp.map(['a', 'b'], lambda cols: np.max([*cols])),
              )
      )
df.print()

```

``` python
shape: (3, 4)
┌─────────────────────────────┐
│   a     b   min_ab   max_ab │
│ i64   i64      i64      i64 │
╞═════════════════════════════╡
│   1     2        1        2 │
│  10   -20      -20       10 │
│ 100   100      100      100 │
└─────────────────────────────┘
```

## Changing many variables {#change-type-of-many-variables-at-once}

There are different ways to change many variables at one. For instance,
consider this data:

``` {.python exports="both" results="output code" tangle="02-mutate.py" cache="yes" noweb="no" session="*Python*" linenums="1"}
# select some rows and varibles
df = (starwars
      .head(5) 
      .select("name", "homeworld", "species")
      )
df.print()

```

``` python
shape: (5, 3)
┌──────────────────────────────────────┐
│ name             homeworld   species │
│ str              str         str     │
╞══════════════════════════════════════╡
│ Luke Skywalker   Tatooine    Human   │
│ C-3PO            Tatooine    Droid   │
│ R2-D2            Naboo       Droid   │
│ Darth Vader      Tatooine    Human   │
│ Leia Organa      Alderaan    Human   │
└──────────────────────────────────────┘
```

To change the type to factor of all variables whose name match `hom` or
`sp` we can use:

``` {.python exports="both" results="output code" tangle="02-mutate.py" cache="yes" noweb="no" session="*Python*" linenums="1"}
# change to factor (i.e., categorical) those whose name matches hom|sp
df = df.mutate(tp.across(tp.matches("hom|sp"),  tp.as_factor, names_suffix="_cat"))
df.print()

```

``` python
shape: (5, 5)
┌────────────────────────────────────────────────────────────────────┐
│ name             homeworld   species   homeworld_cat   species_cat │
│ str              str         str       cat             cat         │
╞════════════════════════════════════════════════════════════════════╡
│ Luke Skywalker   Tatooine    Human     Tatooine        Human       │
│ C-3PO            Tatooine    Droid     Tatooine        Droid       │
│ R2-D2            Naboo       Droid     Naboo           Droid       │
│ Darth Vader      Tatooine    Human     Tatooine        Human       │
│ Leia Organa      Alderaan    Human     Alderaan        Human       │
└────────────────────────────────────────────────────────────────────┘
```

Another possible way is to use a dictionary comprehension. See more
examples [here](../../case-studies//standardizing.md).

## Dynamic variable names {#using-dynamic-variable-names}

We can use dynamic names to create the new variable:

``` {.python exports="both" results="output code" tangle="02-mutate.py" cache="yes" noweb="no" session="*Python*" linenums="1"}

new_var = "mass2_squared"
df = (starwars
      .head(5)
      .select('name', 'mass')
      # create a new variable using a dynamic name:
      .mutate(**{new_var : tp.col('mass') **2 })
      )
df.print()
```

``` python
shape: (5, 3)
┌─────────────────────────────────────────┐
│ name               mass   mass2_squared │
│ str                 f64             f64 │
╞═════════════════════════════════════════╡
│ Luke Skywalker    77.00        5,929.00 │
│ C-3PO             75.00        5,625.00 │
│ R2-D2             32.00        1,024.00 │
│ Darth Vader      136.00       18,496.00 │
│ Leia Organa       49.00        2,401.00 │
└─────────────────────────────────────────┘
```
