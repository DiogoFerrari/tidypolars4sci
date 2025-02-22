# Filter

## Code

Preparing the data sets and setting the data size and the number of
repetitions:

``` {.python exports="code" results="none" tangle="src-filter.py" cache="yes" noweb="no" session="*Python-Org*"}
from docs.src.config import *
from docs.src.performance import *
import time

m = 100              # repetitions
num_rows = 2_000_000 # number of rows

df_tp = tp.tibble({'a':np.random.choice(['apple','banana','carrot',
                                    'date','eggplant'], num_rows), 
                 'b':np.random.rand(num_rows),
                 'c':np.random.rand(num_rows),
                 'd':np.random.rand(num_rows)})
df_pandas = df_tp.to_pandas().copy()
df_polars = df_tp.to_polars()
```

``` {.python exports="code" results="none" tangle="src-filter.py" cache="yes" noweb="no" session="*Python-Org*"}
# collect processing time
processing_time = {'pandas': [],
                   'polars': [],
                   'tidypolars4sci': [],
                   }

# pandas 
# ------
for _ in range(m):
    start_time = time.time()
    df_pandas.query("a=='apple' | a=='banana'")
    processing_time['pandas'] += [time.time() - start_time]

# polars 
# ------
for _ in range(m):
    start_time = time.time()
    df_polars.filter((pl.col('a')=='apple') | (pl.col('a')=='banana'))
    processing_time['polars'] += [time.time() - start_time]

# tidypolars4si
# -------------
for _ in range(m):
    start_time = time.time()
    df_tp.filter((tp.col('a')=='apple') | (tp.col('a')=='banana'))
    processing_time['tidypolars4sci'] += [time.time() - start_time]

```

## Results

``` python
shape: (3, 6)
┌───────────────────────────────────────────────────────────────────────────┐
│ Module           Mean     SD    Min    Max   How much slower than polars? │
│ str               f64    f64    f64    f64   str                          │
╞═══════════════════════════════════════════════════════════════════════════╡
│ polars           0.01   0.00   0.01   0.01   1.0x (baseline)              │
│ tidypolars4sci   0.01   0.00   0.01   0.02   0.9x                         │
│ pandas           0.09   0.00   0.09   0.12   7.4x                         │
└───────────────────────────────────────────────────────────────────────────┘
```

![](./tables-and-figures/filter.png)
