## Creating/Changing Variables {#basic-examples}

To create new variables based on the transformation of existing ones.
Here is the `starwars` dataset provided with the module:

``` {.python exports="both" results="output code" tangle="src-mutate.py" cache="yes" noweb="no" session="*Python*" linenums="1" eval="always"}
import tidypolars4sci as tp
from tidypolars4sci.data import starwars

print(starwars.__doc__)
```

``` python

Starwars characters dataset.

Description
-----------

A dataset containing information on Star Wars characters, originally sourced from SWAPI 
(https://swapi.py4e.com/) and subsequently revised to reflect additional research into 
the gender and sex determinations of characters.

This dataset is structured as a tibble (data frame) with 87 rows and 14 variables.

## Format

+-------------+-------+-------------------------------------------------------------------------------+
| Variable    | Type  | Description                                                                   |
+-------------+-------+-------------------------------------------------------------------------------+
| name        | str   | Name of the character                                                         |
| height      | float | Height in centimeters                                                         |
| mass        | float | Weight in kilograms                                                           |
| hair_color  | str   | Hair color of the character                                                   |
| skin_color  | str   | Skin color of the character                                                   |
| eye_color   | str   | Eye color of the character                                                    |
| birth_year  | str   | Year the character was born, relative to the Battle of Yavin (BBY)            |
| sex         | str   | Biological sex of the character (e.g., male, female, hermaphroditic, or none) |
| gender      | str   | The character's gender role or identity                                       |
| homeworld   | str   | Name of the character's homeworld                                             |
| species     | str   | Name of the character's species                                               |
+-------------+-------+-------------------------------------------------------------------------------+

Notes
-----
The data reflect additional research into the representation of gender and sex in the 
Star Wars universe.

References
----------
* Wickham H (2016). ggplot2: Elegant Graphics for Data Analysis. Springer-Verlag New York.
  ISBN 978-3-319-24277-4, https://ggplot2.tidyverse.org.
```

To see the first rows of the data using head() and print()

``` {.python exports="both" results="output code" tangle="src-mutate.py" cache="yes" noweb="no" session="*Python*" linenums="1" eval="always"}

# 
starwars.head().print()

```

``` python
shape: (5, 11)
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ name             height     mass   hair_color   skin_color    eye_color   birth_year   sex      gender      homeworld   species │
│ cat                 i32      f64   cat          cat           cat                f64   cat      cat         cat         cat     │
╞═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╡
│ Luke Skywalker      172    77.00   blond        fair          blue             19.00   male     masculine   Tatooine    Human   │
│ C-3PO               167    75.00   null         gold          yellow          112.00   none     masculine   Tatooine    Droid   │
│ R2-D2                96    32.00   null         white, blue   red              33.00   none     masculine   Naboo       Droid   │
│ Darth Vader         202   136.00   none         white         yellow           41.90   male     masculine   Tatooine    Human   │
│ Leia Organa         150    49.00   brown        light         brown            19.00   female   feminine    Alderaan    Human   │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

To create new variables and store the results in a new `tibble` called
`df`:

``` {.python exports="both" results="output code" tangle="src-mutate.py" cache="yes" noweb="no" session="*Python*" linenums="1"}
df = (starwars
      # create two new variables:
      .mutate(mass2 = tp.col('mass') * 2,
              mass2_squared = tp.col('mass2') * tp.col('mass2'))
      )
df.head().print()
```

``` python
shape: (5, 13)
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ name             height     mass   hair_color   skin_color    eye_color   birth_year   sex      gender      homeworld   species    mass2   mass2_squared │
│ cat                 i32      f64   cat          cat           cat                f64   cat      cat         cat         cat          f64             f64 │
╞══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╡
│ Luke Skywalker      172    77.00   blond        fair          blue             19.00   male     masculine   Tatooine    Human     154.00       23,716.00 │
│ C-3PO               167    75.00   null         gold          yellow          112.00   none     masculine   Tatooine    Droid     150.00       22,500.00 │
│ R2-D2                96    32.00   null         white, blue   red              33.00   none     masculine   Naboo       Droid      64.00        4,096.00 │
│ Darth Vader         202   136.00   none         white         yellow           41.90   male     masculine   Tatooine    Human     272.00       73,984.00 │
│ Leia Organa         150    49.00   brown        light         brown            19.00   female   feminine    Alderaan    Human      98.00        9,604.00 │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

To change the variable height from centimeters to inches:

``` {.python exports="both" results="output code" tangle="src-mutate.py" cache="yes" noweb="no" session="*Python*" linenums="1" eval="always"}
df = starwars.mutate(height = tp.col("height") /  2.54)
df.head().print()
```

``` python
shape: (5, 11)
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ name             height     mass   hair_color   skin_color    eye_color   birth_year   sex      gender      homeworld   species │
│ cat                 f64      f64   cat          cat           cat                f64   cat      cat         cat         cat     │
╞═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╡
│ Luke Skywalker    67.72    77.00   blond        fair          blue             19.00   male     masculine   Tatooine    Human   │
│ C-3PO             65.75    75.00   null         gold          yellow          112.00   none     masculine   Tatooine    Droid   │
│ R2-D2             37.80    32.00   null         white, blue   red              33.00   none     masculine   Naboo       Droid   │
│ Darth Vader       79.53   136.00   none         white         yellow           41.90   male     masculine   Tatooine    Human   │
│ Leia Organa       59.06    49.00   brown        light         brown            19.00   female   feminine    Alderaan    Human   │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Default Functions

TidyPolars$^{4sci} $ provides many default functions that can be applied
directly to columns. Here is an example:

``` {.python exports="both" results="output code" tangle="src-mutate.py" cache="yes" hlines="yes" colnames="yes" noweb="no" session="*Python*" linenums="1"}
df = (starwars
      .select('name', 'mass')
      .mutate(mass_avg = tp.col('mass').mean(),
              mass_min = tp.col('mass').min()
              )
      )
df.head(5).print()
```

``` python
shape: (5, 4)
┌───────────────────────────────────────────────┐
│ name               mass   mass_avg   mass_min │
│ cat                 f64        f64        f64 │
╞═══════════════════════════════════════════════╡
│ Luke Skywalker    77.00      97.31      15.00 │
│ C-3PO             75.00      97.31      15.00 │
│ R2-D2             32.00      97.31      15.00 │
│ Darth Vader      136.00      97.31      15.00 │
│ Leia Organa       49.00      97.31      15.00 │
└───────────────────────────────────────────────┘
```

The module provides many other default functions to compute summary
statistics of columns and use them in combination with `mutate()` or
`summary()`. Check [Summarize](../statistics/summarize.md) in the User
Guide and [Summary Statistics](../../../reference/stats/abs/) in the API
reference for more information.

## Custom functions

The function `map()` can be used to apply user-defined custom functions.
The result can be stored in a new column of the data frame using
`mutate()`. Here is an example of how to apply custom functions to one
or more columns:

-   Note: the `*` in `*cols` is used to expand the columns. One could
    also use `cols[0], cols[1]` instead. The index follows the order of
    the column names provided in the list before the `lambda` function.

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

## By group

To create variables by group, use `group_by()`. Here is a summary by
four groups `"vs", "am", "gear", 'carb'`:

``` {.python exports="both" results="output code" tangle="src-default-functions.py" cache="yes" hlines="yes" colnames="yes" noweb="no" session="*Python*" linenums="1"}
import tidypolars4sci as tp
from tidypolars4sci.data import mtcars as df

df = (df
 .group_by(["vs", "am", "gear", 'carb'])
 .mutate(disp_avg = tp.col("disp").mean(),
         disp_std = tp.col("disp").std(),
         disp_med = tp.col("disp").median(),
         disp_min = tp.col("disp").min(),
         disp_max = tp.col("disp").max(),
         )
)
df.head().print()

```

``` python
shape: (5, 17)
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ name               mpg   cyl     disp    hp   drat     wt    qsec    vs    am   gear   carb   disp_avg   disp_std   disp_med   disp_min   disp_max │
│ str                f64   i64      f64   i64    f64    f64     f64   i64   i64    i64    i64        f64        f64        f64        f64        f64 │
╞════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╡
│ Mazda RX4        21.00     6   160.00   110   3.90   2.62   16.46     0     1      4      4     160.00       0.00     160.00     160.00     160.00 │
│ Mazda RX4 Wag    21.00     6   160.00   110   3.90   2.88   17.02     0     1      4      4     160.00       0.00     160.00     160.00     160.00 │
│ Datsun 710       22.80     4   108.00    93   3.85   2.32   18.61     1     1      4      1      84.20      16.28      78.85      71.10     108.00 │
│ Fiat 128         32.40     4    78.70    66   4.08   2.20   19.47     1     1      4      1      84.20      16.28      78.85      71.10     108.00 │
│ Toyota Corolla   33.90     4    71.10    65   4.22   1.83   19.90     1     1      4      1      84.20      16.28      78.85      71.10     108.00 │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## By column name match {#change-type-of-many-variables-at-once}

Consider this data:

``` {.python exports="both" results="output code" tangle="02-mutate.py" cache="yes" noweb="no" session="*Python*" linenums="1"}
from tidypolars4sci.data import mtcars as df

df.head(5).print()

```

``` python
shape: (5, 12)
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│ name                  mpg   cyl     disp    hp   drat     wt    qsec    vs    am   gear   carb │
│ str                   f64   i64      f64   i64    f64    f64     f64   i64   i64    i64    i64 │
╞════════════════════════════════════════════════════════════════════════════════════════════════╡
│ Mazda RX4           21.00     6   160.00   110   3.90   2.62   16.46     0     1      4      4 │
│ Mazda RX4 Wag       21.00     6   160.00   110   3.90   2.88   17.02     0     1      4      4 │
│ Datsun 710          22.80     4   108.00    93   3.85   2.32   18.61     1     1      4      1 │
│ Hornet 4 Drive      21.40     6   258.00   110   3.08   3.21   19.44     1     0      3      1 │
│ Hornet Sportabout   18.70     8   360.00   175   3.15   3.44   17.02     0     0      3      2 │
└────────────────────────────────────────────────────────────────────────────────────────────────┘
```

To change variables in the data that contain either \"ar\" or \"dr\" in
their name to categorical type and store the results in the variables
\<original name\>~cat~, use:

``` {.python exports="both" results="output code" tangle="02-mutate.py" cache="yes" noweb="no" session="*Python*" linenums="1"}
df_new = df.mutate(tp.across(tp.matches("ar|dr"),  tp.as_factor, names_suffix="_cat"))
df_new.head().print()

```

``` python
shape: (5, 15)
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ name                  mpg   cyl     disp    hp   drat     wt    qsec    vs    am   gear   carb   drat_cat   gear_cat   carb_cat │
│ str                   f64   i64      f64   i64    f64    f64     f64   i64   i64    i64    i64   cat        cat        cat      │
╞═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╡
│ Mazda RX4           21.00     6   160.00   110   3.90   2.62   16.46     0     1      4      4   3.9        4          4        │
│ Mazda RX4 Wag       21.00     6   160.00   110   3.90   2.88   17.02     0     1      4      4   3.9        4          4        │
│ Datsun 710          22.80     4   108.00    93   3.85   2.32   18.61     1     1      4      1   3.85       4          1        │
│ Hornet 4 Drive      21.40     6   258.00   110   3.08   3.21   19.44     1     0      3      1   3.08       3          1        │
│ Hornet Sportabout   18.70     8   360.00   175   3.15   3.44   17.02     0     0      3      2   3.15       3          2        │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

To store the results in the original variables instead:

``` {.python exports="both" results="output code" tangle="02-mutate.py" cache="yes" noweb="no" session="*Python*" linenums="1"}
df_new = df.mutate(tp.across(tp.matches("ar|dr"),  tp.as_factor))
df_new.head().print()

```

``` python
shape: (5, 12)
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│ name                  mpg   cyl     disp    hp   drat     wt    qsec    vs    am   gear   carb │
│ str                   f64   i64      f64   i64   cat     f64     f64   i64   i64   cat    cat  │
╞════════════════════════════════════════════════════════════════════════════════════════════════╡
│ Mazda RX4           21.00     6   160.00   110   3.9    2.62   16.46     0     1   4      4    │
│ Mazda RX4 Wag       21.00     6   160.00   110   3.9    2.88   17.02     0     1   4      4    │
│ Datsun 710          22.80     4   108.00    93   3.85   2.32   18.61     1     1   4      1    │
│ Hornet 4 Drive      21.40     6   258.00   110   3.08   3.21   19.44     1     0   3      1    │
│ Hornet Sportabout   18.70     8   360.00   175   3.15   3.44   17.02     0     0   3      2    │
└────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## By column type

Consider this data:

``` {.python exports="both" results="output code" tangle="02-mutate.py" cache="yes" noweb="no" session="*Python*" linenums="1"}
from tidypolars4sci.data import mtcars as df

df.head(5).print()

```

``` python
shape: (5, 12)
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│ name                  mpg   cyl     disp    hp   drat     wt    qsec    vs    am   gear   carb │
│ str                   f64   i64      f64   i64    f64    f64     f64   i64   i64    i64    i64 │
╞════════════════════════════════════════════════════════════════════════════════════════════════╡
│ Mazda RX4           21.00     6   160.00   110   3.90   2.62   16.46     0     1      4      4 │
│ Mazda RX4 Wag       21.00     6   160.00   110   3.90   2.88   17.02     0     1      4      4 │
│ Datsun 710          22.80     4   108.00    93   3.85   2.32   18.61     1     1      4      1 │
│ Hornet 4 Drive      21.40     6   258.00   110   3.08   3.21   19.44     1     0      3      1 │
│ Hornet Sportabout   18.70     8   360.00   175   3.15   3.44   17.02     0     0      3      2 │
└────────────────────────────────────────────────────────────────────────────────────────────────┘
```

To change by column type, say, all `integer` columns to `string`:

``` {.python exports="both" results="output code" tangle="src-mutate.py" cache="yes" noweb="no" session="*Python*" linenums="1" eval="always"}
df_new = df.mutate(tp.across(tp.is_integer,  tp.as_string))   # numeric (inteter or float)
df_new.head().print()
```

``` python
shape: (5, 12)
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│ name                  mpg   cyl     disp   hp    drat     wt    qsec   vs    am    gear   carb │
│ str                   f64   str      f64   str    f64    f64     f64   str   str   str    str  │
╞════════════════════════════════════════════════════════════════════════════════════════════════╡
│ Mazda RX4           21.00   6     160.00   110   3.90   2.62   16.46   0     1     4      4    │
│ Mazda RX4 Wag       21.00   6     160.00   110   3.90   2.88   17.02   0     1     4      4    │
│ Datsun 710          22.80   4     108.00   93    3.85   2.32   18.61   1     1     4      1    │
│ Hornet 4 Drive      21.40   6     258.00   110   3.08   3.21   19.44   1     0     3      1    │
│ Hornet Sportabout   18.70   8     360.00   175   3.15   3.44   17.02   0     0     3      2    │
└────────────────────────────────────────────────────────────────────────────────────────────────┘
```

Here are other examples:

``` {.python exports="both" results="output code" tangle="src-mutate.py" cache="yes" noweb="no" session="*Python*" linenums="1" eval="always"}

# --- not printed below -----
order = sorted(df.pull('name').to_list())
df = (df
      .mutate(name_factor = tp.as_factor('name'),
              name_ordered = tp.as_factor('name', order))
      .relocate("name_ordered", after='name')
      .relocate("name_factor", after='name')
      )
df

df.mutate(tp.across(tp.is_character,  tp.as_string)) # string and factor (ordered or unordered)
df.mutate(tp.across(tp.is_factor,  tp.as_string))    # factor (ordered or unordered)
df.mutate(tp.across(tp.is_string,  tp.as_factor))    # only strings
df.mutate(tp.across(tp.is_ordered,  tp.as_string))   # unly ordered factors
df.mutate(tp.across(tp.is_unordered,  tp.as_string)) # only unordered factors

df.mutate(tp.across(tp.is_numeric,  tp.as_factor))   # numeric (inteter or float)
df.mutate(tp.across(tp.is_integer,  tp.as_factor))   # only inteter
df.mutate(tp.across(tp.is_float,  tp.as_factor))     # only float

# any combinarion (e.g., string or float)
df.mutate(tp.across([tp.is_string, tp.is_float], tp.as_factor)) 

# --- printed below ----
df_new = df.mutate(tp.across([tp.is_string, tp.is_float], tp.as_factor)) 
df_new.head().print()

```

``` python
shape: (5, 14)
┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ name                name_factor         name_ordered        mpg    cyl   disp     hp   drat   wt      qsec     vs    am   gear   carb │
│ cat                 cat                 enum                cat    i64   cat     i64   cat    cat     cat     i64   i64    i64    i64 │
╞═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╡
│ Mazda RX4           Mazda RX4           Mazda RX4           21.0     6   160.0   110   3.9    2.62    16.46     0     1      4      4 │
│ Mazda RX4 Wag       Mazda RX4 Wag       Mazda RX4 Wag       21.0     6   160.0   110   3.9    2.875   17.02     0     1      4      4 │
│ Datsun 710          Datsun 710          Datsun 710          22.8     4   108.0    93   3.85   2.32    18.61     1     1      4      1 │
│ Hornet 4 Drive      Hornet 4 Drive      Hornet 4 Drive      21.4     6   258.0   110   3.08   3.215   19.44     1     0      3      1 │
│ Hornet Sportabout   Hornet Sportabout   Hornet Sportabout   18.7     8   360.0   175   3.15   3.44    17.02     0     0      3      2 │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## All columns

Consider this data:

``` {.python exports="both" results="output code" tangle="02-mutate.py" cache="yes" noweb="no" session="*Python*" linenums="1"}
from tidypolars4sci.data import mtcars as df

df.head(5).print()

```

``` python
shape: (5, 12)
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│ name                  mpg   cyl     disp    hp   drat     wt    qsec    vs    am   gear   carb │
│ str                   f64   i64      f64   i64    f64    f64     f64   i64   i64    i64    i64 │
╞════════════════════════════════════════════════════════════════════════════════════════════════╡
│ Mazda RX4           21.00     6   160.00   110   3.90   2.62   16.46     0     1      4      4 │
│ Mazda RX4 Wag       21.00     6   160.00   110   3.90   2.88   17.02     0     1      4      4 │
│ Datsun 710          22.80     4   108.00    93   3.85   2.32   18.61     1     1      4      1 │
│ Hornet 4 Drive      21.40     6   258.00   110   3.08   3.21   19.44     1     0      3      1 │
│ Hornet Sportabout   18.70     8   360.00   175   3.15   3.44   17.02     0     0      3      2 │
└────────────────────────────────────────────────────────────────────────────────────────────────┘
```

To change all columns to factors:

``` {.python exports="both" results="output code" tangle="src-mutate.py" cache="yes" noweb="no" session="*Python*" linenums="1" eval="always"}
df_new = df.mutate(tp.across(tp.everything(),  tp.as_factor))
df_new.head().print()
```

``` python
shape: (5, 12)
┌───────────────────────────────────────────────────────────────────────────────────────────────┐
│ name                mpg    cyl   disp    hp    drat   wt      qsec    vs    am    gear   carb │
│ cat                 cat    cat   cat     cat   cat    cat     cat     cat   cat   cat    cat  │
╞═══════════════════════════════════════════════════════════════════════════════════════════════╡
│ Mazda RX4           21.0   6     160.0   110   3.9    2.62    16.46   0     1     4      4    │
│ Mazda RX4 Wag       21.0   6     160.0   110   3.9    2.875   17.02   0     1     4      4    │
│ Datsun 710          22.8   4     108.0   93    3.85   2.32    18.61   1     1     4      1    │
│ Hornet 4 Drive      21.4   6     258.0   110   3.08   3.215   19.44   1     0     3      1    │
│ Hornet Sportabout   18.7   8     360.0   175   3.15   3.44    17.02   0     0     3      2    │
└───────────────────────────────────────────────────────────────────────────────────────────────┘
```

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
│ cat                 f64             f64 │
╞═════════════════════════════════════════╡
│ Luke Skywalker    77.00        5,929.00 │
│ C-3PO             75.00        5,625.00 │
│ R2-D2             32.00        1,024.00 │
│ Darth Vader      136.00       18,496.00 │
│ Leia Organa       49.00        2,401.00 │
└─────────────────────────────────────────┘
```
