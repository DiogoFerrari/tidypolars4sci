# Summarise

## Code

``` {.python exports="code" results="none" tangle="src-summarise.py" cache="yes" noweb="no" session="*Python-Org*"}
from docs.src.config import *
from docs.src.performance import *
# 
import tidypolars4sci as tp
import time
from numpy.random import uniform as runif
from numpy.random import normal as rnorm

m = 100
n = 2_000_000

df = pl.DataFrame({
    "a": runif(300, 500, n),
    "b": runif(0, 100, n),
    "c": rnorm(0, 1, n),
    "d": runif(100, 200, n),
    "e": rnorm(10, 5, n)
})

```

Preparing the data and collecting processing time:

``` {.python exports="code" results="none" tangle="src-summarise.py" cache="yes" noweb="no" session="*Python-Org*"}


df_tp = tp.from_polars(df)
df_pd = df.to_pandas()
df_pl = df


df_tp.summarise(tp.matches("."), np.mean)

def on_pandas(df):
    df.agg(['mean', 'std']).reset_index()

def on_polars(df):
    mean = df_pl.select([pl.col(col).mean().alias(f"{col}_mean") for col in df.columns])
    std = df_pl.select([pl.col(col).std().alias(f"{col}_std") for col in df.columns])

def on_tidypolars4sci(df):
    df.summarise(**{f"{col}_mean": tp.col(col).mean() for col in df.names},
                 **{f"{col}_std": tp.col(col).std() for col in df.names},
                 )

n = df.nrow    # sample size
m = 1_000      # repetitions

# collect processing time
processing_time = {'pandas': [],
                   'polars': [],
                   'tidypolars4sci': [],
                   }
# 
for i in range(m):
    # pandas
    start_time = time.time()
    on_pandas(df_pd)
    processing_time['pandas'] += [time.time() - start_time]

    # polars
    start_time = time.time()
    on_polars(df_pl)
    processing_time['polars'] += [time.time() - start_time]

    start_time = time.time()
    on_tidypolars4sci(mtcars)
    processing_time['tidypolars4sci'] += [time.time() - start_time]

```

## Results

``` python
shape: (3, 6)
┌───────────────────────────────────────────────────────────────────────────────────────┐
│ Module              Mean        SD       Min       Max   How much slower than polars? │
│ str                  f64       f64       f64       f64   str                          │
╞═══════════════════════════════════════════════════════════════════════════════════════╡
│ polars           0.00047   0.00015   0.00023   0.00143   1.0x (baseline)              │
│ tidypolars4sci   0.00084   0.00024   0.00047   0.00266   1.8x                         │
│ pandas           0.00223   0.00050   0.00152   0.00563   4.8x                         │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

Here is the summary of the performance:

![](./tables-and-figures/summarise.png)
