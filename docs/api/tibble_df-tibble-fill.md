## More Examples

Here are some examples

``` {.python exports="both" results="output code" tangle="src-tibble_df-tibble-arrange.py" cache="yes" noweb="no" session="*Python*" linenums="1" eval="always"}
from tidypolars4sci.data import mtcars as df
import tidypolars4sci as tp

dfsmall = df.mutate(drat=tp.case_when(tp.col('drat')==3.9, None, True, tp.col('drat')),
                    hp_carb = tp.case_when(tp.col('hp')==175, None,
                                           True, tp.col('hp')+tp.col('carb')))\
            .slice(list(range(5)))\
            .select('drat', 'hp', 'carb', 'hp_carb')
dfsmall.print()
```

``` python
shape: (5, 4)
┌─────────────────────────────┐
│ drat    hp   carb   hp_carb │
│  f64   i64    i64       i64 │
╞═════════════════════════════╡
│ null   110      4       114 │
│ null   110      4       114 │
│ 3.85    93      1        94 │
│ 3.08   110      1       111 │
│ 3.15   175      2      null │
└─────────────────────────────┘
```

``` {.python exports="both" results="output code" tangle="src-tibble_df-tibble-fill.py" cache="yes" noweb="no" session="*Python*" linenums="1" eval="always"}
dfsmall.fill('hp_carb').print()
```

``` python
shape: (5, 4)
┌─────────────────────────────┐
│ drat    hp   carb   hp_carb │
│  f64   i64    i64       i64 │
╞═════════════════════════════╡
│ null   110      4       114 │
│ null   110      4       114 │
│ 3.85    93      1        94 │
│ 3.08   110      1       111 │
│ 3.15   175      2       111 │
└─────────────────────────────┘
```

``` {.python exports="both" results="output code" tangle="src-tibble_df-tibble-fill.py" cache="yes" noweb="no" session="*Python*" linenums="1" eval="always"}
dfsmall.fill('drat').print()
```

``` python
shape: (5, 4)
┌─────────────────────────────┐
│ drat    hp   carb   hp_carb │
│  f64   i64    i64       i64 │
╞═════════════════════════════╡
│ null   110      4       114 │
│ null   110      4       114 │
│ 3.85    93      1        94 │
│ 3.08   110      1       111 │
│ 3.15   175      2      null │
└─────────────────────────────┘
```

``` {.python exports="both" results="output code" tangle="src-tibble_df-tibble-fill.py" cache="yes" noweb="no" session="*Python*" linenums="1" eval="always"}
dfsmall.fill('drat', direction='up').print()
```

``` python
shape: (5, 4)
┌─────────────────────────────┐
│ drat    hp   carb   hp_carb │
│  f64   i64    i64       i64 │
╞═════════════════════════════╡
│ 3.85   110      4       114 │
│ 3.85   110      4       114 │
│ 3.85    93      1        94 │
│ 3.08   110      1       111 │
│ 3.15   175      2      null │
└─────────────────────────────┘
```
