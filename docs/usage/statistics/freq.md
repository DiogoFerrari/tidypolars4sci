# Frequency Tables

The method `.freq()` produces tables with relative frequency, joint
relative frequencies, and conditional relative frequencies. The joint
and conditional cases can combine multiple variables. The number of
cases (N), standard deviation (Std.Dev.), and lower (low) and upper
(high) 95% confidence intervals bounds based on normal approximation are
provided.

``` {#freq .python exports="both" results="output code" tangle="freq.py" cache="yes" noweb="no" session="*Python-Org*"}
import tidypolars4sci as tp
from tidypolars4sci.data import mtcars as df

# Notes:
# - .arrange() below is just sorting the rows to facilitate visualization.
# - .print() is used just to display the full table.

# Relative frequencies: P(cyl)
df.freq('cyl').print()
```

``` python
shape: (3, 6)
┌──────────────────────────────────────────────┐
│ cyl     N    Freq   Std.Dev.     low    high │
│ i64   i64     f64        f64     f64     f64 │
╞══════════════════════════════════════════════╡
│   4    11   34.38      14.32    6.31   62.44 │
│   6     7   21.88      15.62   -8.75   52.50 │
│   8    14   43.75      13.26   17.76   69.74 │
└──────────────────────────────────────────────┘
```

``` {.python exports="both" results="output code" tangle="freq.py" cache="yes" noweb="no" session="*Python-Org*"}

# Joint relative frequencies: P(cyl, am)
df.freq(['cyl', 'am']).print()

```

``` python
shape: (6, 7)
┌─────────────────────────────────────────────────────┐
│ cyl    am     N    Freq   Std.Dev.      low    high │
│ i64   i64   i64     f64        f64      f64     f64 │
╞═════════════════════════════════════════════════════╡
│   4     0     3    9.38      16.83   -23.61   42.36 │
│   4     1     8   25.00      15.31    -5.01   55.01 │
│   6     0     4   12.50      16.54   -19.91   44.91 │
│   6     1     3    9.38      16.83   -23.61   42.36 │
│   8     0    12   37.50      13.98    10.11   64.89 │
│   8     1     2    6.25      17.12   -27.30   39.80 │
└─────────────────────────────────────────────────────┘
```

``` {.python exports="both" results="output code" tangle="freq.py" cache="yes" noweb="no" session="*Python-Org*"}
# Conditional relative frequencies given one variable: P(cyl | am)
df.freq('cyl', 'am').arrange('am').print()
```

``` python
shape: (6, 7)
┌─────────────────────────────────────────────────────┐
│  am   cyl     N    Freq   Std.Dev.      low    high │
│ i64   i64   i64     f64        f64      f64     f64 │
╞═════════════════════════════════════════════════════╡
│   0     4     3   15.79      21.05   -25.47   57.05 │
│   0     6     4   21.05      20.38   -18.90   61.01 │
│   0     8    12   63.16      13.93    35.86   90.45 │
│   1     4     8   61.54      17.20    27.83   95.25 │
│   1     6     3   23.08      24.33   -24.60   70.75 │
│   1     8     2   15.38      25.51   -34.62   65.39 │
└─────────────────────────────────────────────────────┘
```

``` {.python exports="both" results="output code" tangle="freq.py" cache="yes" noweb="no" session="*Python-Org*"}
# Conditional relative frequencies given two variables: P(cyl | am, carb)
df.freq('cyl', ['am', 'carb']).arrange('am', 'carb').print()
```

``` python
shape: (13, 8)
┌──────────────────────────────────────────────────────────────┐
│  am   carb   cyl     N     Freq   Std.Dev.      low     high │
│ i64    i64   i64   i64      f64        f64      f64      f64 │
╞══════════════════════════════════════════════════════════════╡
│   0      1     4     1    33.33      47.14   -59.06   125.73 │
│   0      1     6     2    66.67      33.33     1.33   132.00 │
│   0      2     4     2    33.33      33.33   -32.00    98.67 │
│   0      2     8     4    66.67      23.57    20.47   112.86 │
│   0      3     8     3   100.00       0.00   100.00   100.00 │
│   0      4     6     2    28.57      31.94   -34.04    91.18 │
│   0      4     8     5    71.43      20.20    31.83   111.03 │
│   1      1     4     4   100.00       0.00   100.00   100.00 │
│   1      2     4     4   100.00       0.00   100.00   100.00 │
│   1      4     6     2    66.67      33.33     1.33   132.00 │
│   1      4     8     1    33.33      47.14   -59.06   125.73 │
│   1      6     6     1   100.00       0.00   100.00   100.00 │
│   1      8     8     1   100.00       0.00   100.00   100.00 │
└──────────────────────────────────────────────────────────────┘
```

``` {.python exports="both" results="output code" tangle="freq.py" cache="yes" noweb="no" session="*Python-Org*"}
# Joint conditional relative frequencies given two variables: P(cyl, vs | am, carb)
df.freq(['cyl', 'vs'], ['am', 'carb']).arrange('am', 'carb').print()
```

``` python
shape: (14, 9)
┌────────────────────────────────────────────────────────────────────┐
│  am   carb   cyl    vs     N     Freq   Std.Dev.      low     high │
│ i64    i64   i64   i64   i64      f64        f64      f64      f64 │
╞════════════════════════════════════════════════════════════════════╡
│   0      1     4     1     1    33.33      47.14   -59.06   125.73 │
│   0      1     6     1     2    66.67      33.33     1.33   132.00 │
│   0      2     4     1     2    33.33      33.33   -32.00    98.67 │
│   0      2     8     0     4    66.67      23.57    20.47   112.86 │
│   0      3     8     0     3   100.00       0.00   100.00   100.00 │
│   0      4     6     1     2    28.57      31.94   -34.04    91.18 │
│   0      4     8     0     5    71.43      20.20    31.83   111.03 │
│   1      1     4     1     4   100.00       0.00   100.00   100.00 │
│   1      2     4     0     1    25.00      43.30   -59.87   109.87 │
│   1      2     4     1     3    75.00      25.00    26.00   124.00 │
│   1      4     6     0     2    66.67      33.33     1.33   132.00 │
│   1      4     8     0     1    33.33      47.14   -59.06   125.73 │
│   1      6     6     0     1   100.00       0.00   100.00   100.00 │
│   1      8     8     0     1   100.00       0.00   100.00   100.00 │
└────────────────────────────────────────────────────────────────────┘
```
