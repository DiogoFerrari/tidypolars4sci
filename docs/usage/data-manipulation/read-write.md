## Read

Reading files from disk is handled with the function `read_data()`. The
function accepts various formats, including
`csv, xlsx, txt, dta, Rdata, rds, sav` and others. The function accepts
relative paths.

``` {.python exports="both" results="output code" tangle="src-read-write.py" cache="yes" noweb="no" session="*Python*" title="Loading data" linenums="1"}
import tidypolars4sci as tp

fn = "../../src/data/example.csv"
df = tp.read_data(fn=fn)

```

``` python
Loading data 'example.csv'... done!
```

``` {.python exports="both" results="output code" tangle="src-read-write.py" cache="yes" noweb="no" session="*Python*" linenums="1"}

df.head().print()

```

``` python
shape: (3, 2)
┌───────────┐
│   a     b │
│ i64   i64 │
╞═══════════╡
│   1     4 │
│   2     5 │
│   3     6 │
└───────────┘
```

When files type that contain labels of variables and values are loaded,
the function returns a tuple with the data (tibble) and the lables
(dictionary).
