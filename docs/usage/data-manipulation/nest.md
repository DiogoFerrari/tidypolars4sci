## Nested tibbles

It is possible to create nested tibbles using `nest()`:

``` {.python exports="both" results="silent" tangle="src-nest.py" cache="yes" noweb="no" session="*Python*" linenums="1" eval="always"}
import tidypolars4sci as tp
from tidypolars4sci.data import mtcars as df

df = tp.tibble(df)
dfnested = (
    df
    .nest("cyl")
)

dfnested 
# shape: (3, 2)
# ┌───────────────────────┐
# │ cyl   data            │
# │ i64   object          │
# ╞═══════════════════════╡
# │   6   shape: (7, 11)… │
# │   4   shape: (11, 11… │
# │   8   shape: (14, 11… │
# └───────────────────────┘

```

Expanding:

``` {.python exports="both" results="output code" tangle="src-nest.py" cache="yes" noweb="no" session="*Python*" linenums="1" eval="always"}
dfnested.print()
```

``` python
shape: (3, 2)
┌──────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ cyl   data                                                                                           │
│ i64   object                                                                                         │
╞══════════════════════════════════════════════════════════════════════════════════════════════════════╡
│   6   shape: (7, 11)                                                                                 │
│       ┌───────────────────────────────────────────────────────────────────────────────────────┐      │
│       │ name               mpg     disp    hp   drat     wt    qsec    vs    am   gear   carb │      │
│       │ str                f64      f64   i64    f64    f64     f64   i64   i64    i64    i64 │      │
│       ╞═══════════════════════════════════════════════════════════════════════════════════════╡      │
│       │ Mazda RX4        21.00   160.00   110   3.90   2.62   16.46     0     1      4      4 │      │
│       │ Mazda RX4 Wag    21.00   160.00   110   3.90   2.88   17.02     0     1      4      4 │      │
│       │ Hornet 4 Drive   21.40   258.00   110   3.08   3.21   19.44     1     0      3      1 │      │
│       │ Valiant          18.10   225.00   105   2.76   3.46   20.22     1     0      3      1 │      │
│       │ Merc 280         19.20   167.60   123   3.92   3.44   18.30     1     0      4      4 │      │
│       │ Merc 280C        17.80   167.60   123   3.92   3.44   18.90     1     0      4      4 │      │
│       │ Ferrari Dino     19.70   145.00   175   3.62   2.77   15.50     0     1      5     …         │
│   4   shape: (11, 11)                                                                                │
│       ┌───────────────────────────────────────────────────────────────────────────────────────┐      │
│       │ name               mpg     disp    hp   drat     wt    qsec    vs    am   gear   carb │      │
│       │ str                f64      f64   i64    f64    f64     f64   i64   i64    i64    i64 │      │
│       ╞═══════════════════════════════════════════════════════════════════════════════════════╡      │
│       │ Datsun 710       22.80   108.00    93   3.85   2.32   18.61     1     1      4      1 │      │
│       │ Merc 240D        24.40   146.70    62   3.69   3.19   20.00     1     0      4      2 │      │
│       │ Merc 230         22.80   140.80    95   3.92   3.15   22.90     1     0      4      2 │      │
│       │ Fiat 128         32.40    78.70    66   4.08   2.20   19.47     1     1      4      1 │      │
│       │ Honda Civic      30.40    75.70    52   4.93   1.61   18.52     1     1      4      2 │      │
│       │ Toyota Corolla   33.90    71.10    65   4.22   1.83   19.90     1     1      4      1 │      │
│       │ Toyota Corona    21.50   120.10    97   3.70   2.46   20.01     1     0      3    …          │
│   8   shape: (14, 11)                                                                                │
│       ┌────────────────────────────────────────────────────────────────────────────────────────────┐ │
│       │ name                    mpg     disp    hp   drat     wt    qsec    vs    am   gear   carb │ │
│       │ str                     f64      f64   i64    f64    f64     f64   i64   i64    i64    i64 │ │
│       ╞════════════════════════════════════════════════════════════════════════════════════════════╡ │
│       │ Hornet Sportabout     18.70   360.00   175   3.15   3.44   17.02     0     0      3      2 │ │
│       │ Duster 360            14.30   360.00   245   3.21   3.57   15.84     0     0      3      4 │ │
│       │ Merc 450SE            16.40   275.80   180   3.07   4.07   17.40     0     0      3      3 │ │
│       │ Merc 450SL            17.30   275.80   180   3.07   3.73   17.60     0     0      3      3 │ │
│       │ Merc 450SLC           15.20   275.80   180   3.07   3.78   18.00     0     0      3      3 │ │
│       │ Cadillac Fleetwood    10.40   472.00   205   2.93   5.25   17.98     0     0      3      4 │ │
│       │ Lincoln Continental   10.40   46…                                                            │
└──────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Models Nested

Here is an example of using `nest()` for a tidy model estimation:

``` {.python exports="both" results="silent" tangle="src-nest.py" cache="yes" noweb="no" session="*Python*" linenums="1" eval="always"}
from statsmodels.formula.api import ols as lm

def estimate(formula, data):
    return lm(formula, data=data.to_pandas()).fit()

df
mod = (
    df
    .nest('am')
    .mutate(
        formula = tp.case_when(tp.col('am')==1, "wt ~ hp",
                               True, 'wt ~ hp**2'),
        fit = tp.map(['formula', 'data'], lambda row: estimate(*row))
    )
)
mod

# shape: (2, 3)
# ┌───────────────────────┐
# │  am   data     fit    │
# │ i64   object   object │
# ╞═══════════════════════╡
# │   1   shape…   <stat… │
# │   0   shape…   <stat… │
# └───────────────────────┘

```

To extract information from the model, let us say the AIC, and store it
in the table:

``` {.python exports="both" results="output code" tangle="src-nest.py" cache="yes" noweb="no" session="*Python*" linenums="1" eval="always"}
print(
    mod
    .mutate(aic = tp.map(['fit'], lambda row: row[0].aic))
)
```

``` python
shape: (2, 5)
┌────────────────────────────────────────┐
│  am   data     formu…   fit        aic │
│ i64   object   str      object     f64 │
╞════════════════════════════════════════╡
│   1   shape…   wt ~ …   <stat…   13.14 │
│   0   shape…   wt ~ …   <stat…   35.54 │
└────────────────────────────────────────┘
```

To get the summary:

``` {.python exports="both" results="output code" tangle="src-nest.py" cache="yes" noweb="no" session="*Python*" linenums="1" eval="always"}
print(mod.pull('fit')[0].summary())
```

``` python
                            OLS Regression Results                            
==============================================================================
Dep. Variable:                     wt   R-squared:                       0.663
Model:                            OLS   Adj. R-squared:                  0.633
Method:                 Least Squares   F-statistic:                     21.69
Date:                Wed, 19 Nov 2025   Prob (F-statistic):           0.000697
Time:                        00:41:56   Log-Likelihood:                -4.5693
No. Observations:                  13   AIC:                             13.14
Df Residuals:                      11   BIC:                             14.27
Df Model:                           1                                         
Covariance Type:            nonrobust                                         
==============================================================================
                 coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
Intercept      1.6527      0.193      8.561      0.000       1.228       2.078
hp             0.0060      0.001      4.657      0.001       0.003       0.009
==============================================================================
Omnibus:                        2.313   Durbin-Watson:                   1.338
Prob(Omnibus):                  0.315   Jarque-Bera (JB):                0.671
Skew:                          -0.516   Prob(JB):                        0.715
Kurtosis:                       3.418   Cond. No.                         280.
==============================================================================

Notes:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
```
