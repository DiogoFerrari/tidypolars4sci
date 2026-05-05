## More Examples

Here are some examples

``` {.python exports="both" results="output code" tangle="src-tibble_df-tibble-arrange.py" cache="yes" noweb="no" session="*Python*" linenums="1" eval="always"}
from tidypolars4sci.data import mtcars as df
import tidypolars4sci as tp

dfsmall = df.mutate(drat=tp.case_when(tp.col('drat')==3.9, None, True, tp.col('drat')),
                    hp_carb = tp.case_when(tp.col('hp')==175, None,
                                           True, tp.col('hp')+tp.col('carb')))\
            .slice(list(range(5)))
dfsmall.print()

```

``` python
shape: (5, 13)
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ name                  mpg   cyl     disp    hp   drat     wt    qsec    vs    am   gear   carb   hp_carb │
│ str                   f64   i64      f64   i64    f64    f64     f64   i64   i64    i64    i64       i64 │
╞══════════════════════════════════════════════════════════════════════════════════════════════════════════╡
│ Mazda RX4           21.00     6   160.00   110   null   2.62   16.46     0     1      4      4       114 │
│ Mazda RX4 Wag       21.00     6   160.00   110   null   2.88   17.02     0     1      4      4       114 │
│ Datsun 710          22.80     4   108.00    93   3.85   2.32   18.61     1     1      4      1        94 │
│ Hornet 4 Drive      21.40     6   258.00   110   3.08   3.21   19.44     1     0      3      1       111 │
│ Hornet Sportabout   18.70     8   360.00   175   3.15   3.44   17.02     0     0      3      2      null │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

Arranging by the column `name`:

``` {.python exports="both" results="output code" tangle="src-tibble_df-tibble-drop_null.py" cache="yes" noweb="no" session="*Python*" linenums="1" eval="always"}
dfsmall.drop_null().print()
```

``` python
shape: (2, 13)
┌───────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ name               mpg   cyl     disp    hp   drat     wt    qsec    vs    am   gear   carb   hp_carb │
│ str                f64   i64      f64   i64    f64    f64     f64   i64   i64    i64    i64       i64 │
╞═══════════════════════════════════════════════════════════════════════════════════════════════════════╡
│ Datsun 710       22.80     4   108.00    93   3.85   2.32   18.61     1     1      4      1        94 │
│ Hornet 4 Drive   21.40     6   258.00   110   3.08   3.21   19.44     1     0      3      1       111 │
└───────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

``` {.python exports="both" results="output code" tangle="src-tibble_df-tibble-drop_null.py" cache="yes" noweb="no" session="*Python*" linenums="1" eval="always"}
dfsmall.drop_null('hp_carb').print()
```

``` python
shape: (4, 13)
┌───────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ name               mpg   cyl     disp    hp   drat     wt    qsec    vs    am   gear   carb   hp_carb │
│ str                f64   i64      f64   i64    f64    f64     f64   i64   i64    i64    i64       i64 │
╞═══════════════════════════════════════════════════════════════════════════════════════════════════════╡
│ Mazda RX4        21.00     6   160.00   110   null   2.62   16.46     0     1      4      4       114 │
│ Mazda RX4 Wag    21.00     6   160.00   110   null   2.88   17.02     0     1      4      4       114 │
│ Datsun 710       22.80     4   108.00    93   3.85   2.32   18.61     1     1      4      1        94 │
│ Hornet 4 Drive   21.40     6   258.00   110   3.08   3.21   19.44     1     0      3      1       111 │
└───────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

``` {.python exports="both" results="output code" tangle="src-tibble_df-tibble-drop_null.py" cache="yes" noweb="no" session="*Python*" linenums="1" eval="always"}
dfsmall.drop_null('hp').print()
```

``` python
shape: (5, 13)
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ name                  mpg   cyl     disp    hp   drat     wt    qsec    vs    am   gear   carb   hp_carb │
│ str                   f64   i64      f64   i64    f64    f64     f64   i64   i64    i64    i64       i64 │
╞══════════════════════════════════════════════════════════════════════════════════════════════════════════╡
│ Mazda RX4           21.00     6   160.00   110   null   2.62   16.46     0     1      4      4       114 │
│ Mazda RX4 Wag       21.00     6   160.00   110   null   2.88   17.02     0     1      4      4       114 │
│ Datsun 710          22.80     4   108.00    93   3.85   2.32   18.61     1     1      4      1        94 │
│ Hornet 4 Drive      21.40     6   258.00   110   3.08   3.21   19.44     1     0      3      1       111 │
│ Hornet Sportabout   18.70     8   360.00   175   3.15   3.44   17.02     0     0      3      2      null │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
