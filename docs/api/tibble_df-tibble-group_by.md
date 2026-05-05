## More Examples

Here are some examples.

``` {.python exports="both" results="output code" tangle="src-tibble_df-tibble-arrange.py" cache="yes" noweb="no" session="*Python*" linenums="1" eval="always"}
from tidypolars4sci.data import mtcars as df
import tidypolars4sci as tp

# summarizing by group
res = (
    df
    .group_by('cyl')
    .summarize(avg_am = tp.col('am').mean())
)
res.print()
```

``` python
shape: (3, 2)
┌──────────────┐
│ cyl   avg_am │
│ i64      f64 │
╞══════════════╡
│   6     0.43 │
│   4     0.73 │
│   8     0.14 │
└──────────────┘
```

``` {.python exports="both" results="output code" tangle="src-tibble_df-tibble-group_by.py" cache="yes" noweb="no" session="*Python*" linenums="1" eval="always"}
# create new variable by group
res = (
    df
    .group_by('hp')
    .mutate(a = tp.col('am').mean())
)
res.head().print()

```

``` python
shape: (5, 13)
┌───────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ name                  mpg   cyl     disp    hp   drat     wt    qsec    vs    am   gear   carb      a │
│ str                   f64   i64      f64   i64    f64    f64     f64   i64   i64    i64    i64    f64 │
╞═══════════════════════════════════════════════════════════════════════════════════════════════════════╡
│ Mazda RX4           21.00     6   160.00   110   3.90   2.62   16.46     0     1      4      4   0.67 │
│ Mazda RX4 Wag       21.00     6   160.00   110   3.90   2.88   17.02     0     1      4      4   0.67 │
│ Hornet 4 Drive      21.40     6   258.00   110   3.08   3.21   19.44     1     0      3      1   0.67 │
│ Datsun 710          22.80     4   108.00    93   3.85   2.32   18.61     1     1      4      1   1.00 │
│ Hornet Sportabout   18.70     8   360.00   175   3.15   3.44   17.02     0     0      3      2   0.33 │
└───────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
