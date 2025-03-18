# Standardizing variables

It is easy to standardize the value of many varibles at once, or create
new variables standardized. Consider these variables:

``` {.python exports="both" results="output code" tangle="src-mutate.py" cache="yes" hlines="yes" colnames="yes" noweb="no" session="*Python-Org*"}
import tidypolars4sci as tp
from tidypolars4sci.data import starwars as df

# let us select 3 variables and the first 10 rows only for the example
df = df.select('name', 'height', 'mass').slice(list(range(10)))
df.print()
```

``` python
shape: (10, 3)
┌──────────────────────────────────────┐
│ name                 height     mass │
│ str                     i64      f64 │
╞══════════════════════════════════════╡
│ Luke Skywalker          172    77.00 │
│ C-3PO                   167    75.00 │
│ R2-D2                    96    32.00 │
│ Darth Vader             202   136.00 │
│ Leia Organa             150    49.00 │
│ Owen Lars               178   120.00 │
│ Beru Whitesun Lars      165    75.00 │
│ R5-D4                    97    32.00 │
│ Biggs Darklighter       183    84.00 │
│ Obi-Wan Kenobi          182    77.00 │
└──────────────────────────────────────┘
```

To standardize one specific varible:

``` {.python exports="both" results="output code" tangle="src-standardizing.py" cache="yes" hlines="yes" colnames="yes" noweb="no" session="*Python-Org*"}
df.mutate(mass_std = tp.scale("mass")).print()
```

``` python
shape: (10, 4)
┌─────────────────────────────────────────────────┐
│ name                 height     mass   mass_std │
│ str                     i64      f64        f64 │
╞═════════════════════════════════════════════════╡
│ Luke Skywalker          172    77.00       0.04 │
│ C-3PO                   167    75.00      -0.02 │
│ R2-D2                    96    32.00      -1.30 │
│ Darth Vader             202   136.00       1.79 │
│ Leia Organa             150    49.00      -0.79 │
│ Owen Lars               178   120.00       1.32 │
│ Beru Whitesun Lars      165    75.00      -0.02 │
│ R5-D4                    97    32.00      -1.30 │
│ Biggs Darklighter       183    84.00       0.25 │
│ Obi-Wan Kenobi          182    77.00       0.04 │
└─────────────────────────────────────────────────┘
```

To standardize `height` and `mass`, we could do:

``` {.python exports="both" results="output code" tangle="src-mutate.py" cache="yes" hlines="yes" colnames="yes" noweb="no" session="*Python-Org*"}
vars = ['height', 'mass']
tab = df.mutate(**{f"{var}_std": tp.scale(var) for var in vars})
tab.print()
```

``` python
shape: (10, 5)
┌──────────────────────────────────────────────────────────────┐
│ name                 height     mass   height_std   mass_std │
│ str                     i64      f64          f64        f64 │
╞══════════════════════════════════════════════════════════════╡
│ Luke Skywalker          172    77.00         0.36       0.04 │
│ C-3PO                   167    75.00         0.22      -0.02 │
│ R2-D2                    96    32.00        -1.77      -1.30 │
│ Darth Vader             202   136.00         1.20       1.79 │
│ Leia Organa             150    49.00        -0.26      -0.79 │
│ Owen Lars               178   120.00         0.53       1.32 │
│ Beru Whitesun Lars      165    75.00         0.16      -0.02 │
│ R5-D4                    97    32.00        -1.74      -1.30 │
│ Biggs Darklighter       183    84.00         0.67       0.25 │
│ Obi-Wan Kenobi          182    77.00         0.64       0.04 │
└──────────────────────────────────────────────────────────────┘
```

Or we could use `tp.across()`

``` {.python exports="both" results="output code" tangle="src-standardizing.py" cache="yes" hlines="yes" colnames="yes" noweb="no" session="*Python-Org*"}
tab = df.mutate(tp.across(tp.matches("heig|mass"),  tp.scale, names_suffix='_std'))
tab.print()
```

``` python
shape: (10, 5)
┌──────────────────────────────────────────────────────────────┐
│ name                 height     mass   height_std   mass_std │
│ str                     i64      f64          f64        f64 │
╞══════════════════════════════════════════════════════════════╡
│ Luke Skywalker          172    77.00         0.36       0.04 │
│ C-3PO                   167    75.00         0.22      -0.02 │
│ R2-D2                    96    32.00        -1.77      -1.30 │
│ Darth Vader             202   136.00         1.20       1.79 │
│ Leia Organa             150    49.00        -0.26      -0.79 │
│ Owen Lars               178   120.00         0.53       1.32 │
│ Beru Whitesun Lars      165    75.00         0.16      -0.02 │
│ R5-D4                    97    32.00        -1.74      -1.30 │
│ Biggs Darklighter       183    84.00         0.67       0.25 │
│ Obi-Wan Kenobi          182    77.00         0.64       0.04 │
└──────────────────────────────────────────────────────────────┘
```
