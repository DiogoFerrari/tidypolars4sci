# Regression Table

## Motivating example

Regression tables with multiple models displayed in the table columns
are common in academic publications, and they usually follow the same
standard format. The table below is an example from Fournier, Soroka,
and Nir (2020) showing the effect of negative and positive televised
news reports and political ideology on people\'s emotional arousal and
activation, captured by physiological galvanic skin activity. It is easy
to produce this type of table with tidypolars$^{4sci}$, keeping
everything in a tidy format.

![](./tables-and-figures/fournier2020negativity-table-3.png)

## Data

The synthetic data `vote` contains information about Democratic and
Republican voters, including demographics and voting behavior:

``` {.python exports="both" results="output code" tangle="src-regression-table.py" cache="yes" hlines="yes" colnames="yes" noweb="no" session="*Python*" title="Loading data and modules" linenums="1"}
import tidypolars4sci as tp
import tools4sci as t4
from tidypolars4sci.data import vote as df
import numpy as np
# 
from statsmodels.formula.api import ols as lm
from statsmodels.formula.api import glm as glm
from statsmodels.api import families as family

# variables:
df.__codebook__.print()

```

``` python
shape: (9, 3)
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Variable            Type    Description                                                                                  │
│ str                 str     str                                                                                          │
╞══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╡
│ age                 int     Age                                                                                          │
│ income              float   Income (standardized)                                                                        │
│ gender              int     Gender (Male=0; Female=1)                                                                    │
│ ideology            float   Ideology self-placement (left=-10 to right=10)                                               │
│ treatment           int     Treatment group (treated=1; control=0)                                                       │
│ group               str     Group                                                                                        │
│ partisanship        str     Partisanship (Democrat or Republican)                                                        │
│ vote_conservative   int     Voted for the most conservative in-party candidate (Yes=1, No=0)                             │
│ rate_conservative   float   Voters rate of the most conservative in-party candidate (Dislike=low value; Like=high value) │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Estimating

Here are the functions for the estimation, prediction, and summarizing:

``` {.python exports="code" results="none" tangle="src-regression-table.py" cache="yes" hlines="yes" colnames="yes" noweb="no" session="*Python*" title="Functions for estimation, summary, and prediction" linenums="1"}

def create_formula(outcome, adjusted):
    if adjusted:
        # Adjustments are hard-coded here but could have been provided
        # as arguments for the function instead.
        adjustments = "income + age + gender"
    else:
        adjustments = "1"
    formula = f"{outcome} ~ treatment * ideology + {adjustments}"
    return formula

def estimate(data, model, formula):
    # need to covert to pandas for statsmodels
    data = data.to_pandas()
    if model == 'Linear':
        res = lm(formula, data=data).fit()
    else:
        # logit  model with clustered std. errors by the variable 'group'
        res = glm(formula, data=data, family=family.Binomial()).fit(cov_type="cluster",
                                                                    cov_kwds={"groups": data["group"]})
    return res

def get_summary(fit):
    res = fit.summary2().tables[1].reset_index(drop=False, names='term')
    return tp.from_pandas(res)

def predict(fit, data, at):
    newdata = t4.simulate.newdata(data, at=at)
    pred = fit.get_prediction(newdata.to_pandas()).summary_frame(alpha=0.05)
    return newdata.bind_cols(tp.from_pandas(pred))


```

And here is how to run the estimation in tidypolars$^{4sci} $ and
produce a table with tidy results (click on the (+) sign to see code
comments):

``` {.python exports="code" results="none" tangle="src-regression-table.py" cache="yes" hlines="yes" colnames="yes" noweb="no" session="*Python*" title="Tidy estimation, summary, and prediction" linenums="1"}

res = (df
       .nest('partisanship') # (1)!
       .crossing(outcome = ['rate_conservative', "vote_conservative"], # (2)!
                 adjusted = ['Yes', 'No'])
       .mutate(
           model = tp.case_when(tp.col("outcome").str.contains('rate'), 'Linear', # (3)!
                                tp.col("outcome").str.contains('vote'), 'Logit'),
           formula = tp.map(['outcome', 'adjusted'], lambda row: create_formula(*row))) # (4)!
       .mutate(
           fit     = tp.map(['data', 'model', 'formula'], lambda row: estimate(*row)), # (5)!
           summ    = tp.map(["fit"], lambda fit: get_summary(*fit)), # (6)!
           pred    = tp.map(["fit", "data"], lambda row: predict(*row,
                                                                 at={'treatment':[0, 1],
                                                                     'ideology':range(-10, 10)}))  # (7)!
       )
       )
```

1.  Nest the data by partisanship.
2.  `crossing()` expands (replicates) each row of the nested data for
    different outcomes and an indicator of whether the model uses
    adjustment variables.
3.  This variable indicates which model is estimated depending on the
    outcome variable: `rate_conservative` (continuous) uses a linear
    model; `vote_conservative` (binary) uses a logit model.
4.  The function `map()` performs a row-wise operation, creating the
    regression formula depending on the outcome and whether the
    estimation is adjusted; the star (\*) used in `*row` unpacks the
    columns for the function `create_formula()`.
5.  Fit the models in each row.
6.  Create a tidy summary (tibble) for each estimated model in the rows.
7.  Create tables (tibbles) with predicted values at specified values of
    the predictors `treatment` and `ideology`.

``` {.python exports="both" results="value code" tangle="src-regression-table.py" cache="yes" noweb="no" session="*Python*" title="Check the resulting tibble" linenums="1"}
res
```

``` python
shape: (8, 9)
┌────────────────────────────────────────────────────────────────────────────────┐
│ parti…   data     outco…   adjus…   model    formu…   fit      summ     pred   │
│ str      object   str      str      str      str      object   object   object │
╞════════════════════════════════════════════════════════════════════════════════╡
│ repub…   shape…   rate_…   Yes      Linea…   rate_…   <stat…   shape…   shape… │
│ repub…   shape…   rate_…   No       Linea…   rate_…   <stat…   shape…   shape… │
│ repub…   shape…   vote_…   Yes      Logit    vote_…   <stat…   shape…   shape… │
│ …        …        …        …        …        …        …        …        …      │
│ democ…   shape…   rate_…   No       Linea…   rate_…   <stat…   shape…   shape… │
│ democ…   shape…   vote_…   Yes      Logit    vote_…   <stat…   shape…   shape… │
│ democ…   shape…   vote_…   No       Logit    vote_…   <stat…   shape…   shape… │
└────────────────────────────────────────────────────────────────────────────────┘
```

## Summarizing

### Single model

Let us see `statmmodel` summary the results for a particular model:

``` {.python exports="both" results="value code" tangle="src-regression-table.py" cache="yes" noweb="no" session="*Python*" linenums="1"}
pty = 'democrat'
model = 'Logit'
adjusted = 'Yes'
tab = (res
       .filter(tp.col("partisanship")==pty)
       .filter(tp.col("model")==model)
       .filter(tp.col("adjusted")==adjusted)
       .pull('fit')
       )

# result of the first model estimated
tab[0].summary()
```

``` python
                 Generalized Linear Model Regression Results                  
==============================================================================
Dep. Variable:      vote_conservative   No. Observations:                 1017
Model:                            GLM   Df Residuals:                     1010
Model Family:                Binomial   Df Model:                            6
Link Function:                  Logit   Scale:                          1.0000
Method:                          IRLS   Log-Likelihood:                -512.79
Date:                Thu, 06 Mar 2025   Deviance:                       1025.6
Time:                        18:07:44   Pearson chi2:                 1.02e+03
No. Iterations:                     5   Pseudo R-squ. (CS):             0.2843
Covariance Type:              cluster                                         
======================================================================================
                         coef    std err          z      P>|z|      [0.025      0.975]
--------------------------------------------------------------------------------------
Intercept             -0.1600      0.159     -1.008      0.314      -0.471       0.151
treatment             -0.4336      0.092     -4.724      0.000      -0.613      -0.254
ideology              -0.0805      0.031     -2.562      0.010      -0.142      -0.019
treatment:ideology    -0.2886      0.043     -6.765      0.000      -0.372      -0.205
income                -0.0467      0.064     -0.731      0.465      -0.172       0.079
age                    0.0200      0.005      3.972      0.000       0.010       0.030
gender                -0.1203      0.124     -0.967      0.333      -0.364       0.123
======================================================================================
```

Here is the tidy summary:

``` python
shape: (7, 7)
┌─────────────────────────────────────────────────────────────────────────┐
│ term                 Coef.   Std.Err.       z   P>|z|   [0.025   0.975] │
│ str                    f64        f64     f64     f64      f64      f64 │
╞═════════════════════════════════════════════════════════════════════════╡
│ Intercept            -0.16       0.16   -1.01    0.31    -0.47     0.15 │
│ treatment            -0.43       0.09   -4.72    0.00    -0.61    -0.25 │
│ ideology             -0.08       0.03   -2.56    0.01    -0.14    -0.02 │
│ treatment:ideology   -0.29       0.04   -6.76    0.00    -0.37    -0.20 │
│ income               -0.05       0.06   -0.73    0.46    -0.17     0.08 │
│ age                   0.02       0.01    3.97    0.00     0.01     0.03 │
│ gender               -0.12       0.12   -0.97    0.33    -0.36     0.12 │
└─────────────────────────────────────────────────────────────────────────┘
```

### Multiple models

The goal is to create something like this:

![](./tables-and-figures/regression-table-latex-1.png)

To create a regression table with different models displayed in the
columns, formatted for publication, we can use the function
`models2tab()` from the model `tools4sci`. One of the outcomes will be a
`tibble` with the models (`tab`), the other a string with the latex
table (`tabl`). The function uses a dictionary with the estimated
models. The keys are the column names. Line breaks with `\n` can be
used.

``` {.python exports="both" results="output code" tangle="src-regression-table.py" cache="yes" hlines="yes" colnames="yes" noweb="no" session="*Python*"}

# select the models that will show in the table
mods = res.filter(tp.col("partisanship")=='democrat')

# prepare the dictionary (keys will be column names)
mods = {f"Model {m}\nAdjusted: {a}" : fit
        for m, a, fit in zip(mods.pull('model'),
                             mods.pull('adjusted'),
                             mods.pull('fit'))
        }
mods

# from the tools4sci module
tab, tabl = t4.report.models2tab(mods,
                                 latex=True,
                                 # we can rename covariates
                                 covar_labels={"income": "Income (std)"},
                                 kws_latex={'caption': "Example table",
                                            'label': "tab-example",
                                            'header':None,
                                            'align':"lcccc",
                                            'escape':True,
                                            'longtable':False,
                                            'rotate':False
                                            },
                                 sanitize='partial'
                                 )

# here is the tidy table (one can save it in xlsx, or csv)
tab.print()

```

``` python
shape: (20, 5)
┌────────────────────────────────────────────────────────────────────────────────────┐
│                        Model Linear    Model Linear   Model Logit     Model Logit  │
│ str                    Adjusted: Yes   Adjusted: No   Adjusted: Yes   Adjusted: No │
│                        str             str            str             str          │
╞════════════════════════════════════════════════════════════════════════════════════╡
│ Intercept              -0.1194         -0.1194        -0.1600         -0.1600      │
│                        (0.1030)        (0.1030)       (0.1588)        (0.1588)     │
│ treatment              -0.5137***      -0.5137***     -0.4336***      -0.4336***   │
│                        (0.0609)        (0.0609)       (0.0918)        (0.0918)     │
│ ideology               -0.1021***      -0.1021***     -0.0805*        -0.0805*     │
│                        (0.0074)        (0.0074)       (0.0314)        (0.0314)     │
│ treatment x ideology   -0.2804***      -0.2804***     -0.2886***      -0.2886***   │
│                        (0.0104)        (0.0104)       (0.0427)        (0.0427)     │
│ Income (std)           0.0348          0.0348         -0.0467         -0.0467      │
│                        (0.0307)        (0.0307)       (0.0639)        (0.0639)     │
│ age                    0.0234***       0.0234***      0.0200***       0.0200***    │
│                        (0.0020)        (0.0020)       (0.0050)        (0.0050)     │
│ gender                 -0.5098***      -0.5098***     -0.1203         -0.1203      │
│                        (0.0610)        (0.0610)       (0.1244)        (0.1244)     │
│ N. Obs.                1017            1017           1017            1017         │
│ R2 (adj)               0.7641          0.7641                                      │
│ R2 (pseudo)                                           0.2843          0.2843       │
│ BIC                    2859.2311       2859.2311      -5968.2760      -5968.2760   │
│ AIC                    2824.7588       2824.7588      1039.5825       1039.5825    │
│ Std. Error             Classical       Classical      Clustered       Clustered    │
└────────────────────────────────────────────────────────────────────────────────────┘
```

And here is the latex version (note the footnote with p-values; it can
be changed using the parameter footnote of the function
`t4.report.models2tab()` of the `tools4sci` module):

```{=latex}
\begin{table}[!htb]
\caption{Example table}
\label{tab-example}
\centering
\resizebox{\ifdim\width>\linewidth\linewidth\else\width\fi}{!}{
\begin{tabular}{lcccc}
\toprule
  & \makecell{Model Linear\\Adjusted: Yes} & \makecell{Model Linear\\Adjusted: No} & \makecell{Model Logit\\Adjusted: Yes} & \makecell{Model Logit\\Adjusted: No}\\
\midrule
Intercept  &  -0.1194   &  -0.1194   &  -0.1600   &  -0.1600  \\
  &  (0.1030)  &  (0.1030)  &  (0.1588)  &  (0.1588) \\
treatment  &  -0.5137***  &  -0.5137***  &  -0.4336***  &  -0.4336*** \\
  &  (0.0609)  &  (0.0609)  &  (0.0918)  &  (0.0918) \\
ideology  &  -0.1021***  &  -0.1021***  &  -0.0805*  &  -0.0805* \\
  &  (0.0074)  &  (0.0074)  &  (0.0314)  &  (0.0314) \\
treatment x ideology  &  -0.2804***  &  -0.2804***  &  -0.2886***  &  -0.2886*** \\
  &  (0.0104)  &  (0.0104)  &  (0.0427)  &  (0.0427) \\
Income (std)  &  0.0348   &  0.0348   &  -0.0467   &  -0.0467  \\
  &  (0.0307)  &  (0.0307)  &  (0.0639)  &  (0.0639) \\
age  &  0.0234***  &  0.0234***  &  0.0200***  &  0.0200*** \\
  &  (0.0020)  &  (0.0020)  &  (0.0050)  &  (0.0050) \\
gender  &  -0.5098***  &  -0.5098***  &  -0.1203   &  -0.1203  \\
  &  (0.0610)  &  (0.0610)  &  (0.1244)  &  (0.1244) \\
N. Obs.  &  1017  &  1017  &  1017  &  1017 \\
R2 (adj)  &  0.7641  &  0.7641  &    &   \\
R2 (pseudo)  &    &    &  0.2843  &  0.2843 \\
BIC  &  2859.2311  &  2859.2311  &  -5968.2760  &  -5968.2760 \\
AIC  &  2824.7588  &  2824.7588  &  1039.5825  &  1039.5825 \\
Std. Error  &  Classical  &  Classical  &  Clustered  &  Clustered \\
\bottomrule
\multicolumn{5}{r}{+ $p<0.1$; * $p<0.05$; ** $p<0.01$; *** $p<0.001$}\\
\end{tabular}}
\end{table}
```
## Bonus

### Grouping rows

We can group the rows in the table by post-processing the `tibble`
outcome from the `models2tab()` function using tidypolars$^{4sci} $
function `to_latex()`. Something like this:

![](./tables-and-figures/regression-table-latex-1-grouped-rows.png)

We need to create a column indicating the row group:

``` {.python exports="both" results="output code" tangle="src-regression-table.py" cache="yes" hlines="yes" colnames="yes" noweb="no" session="*Python*"}

tab_rows_grouped = tab.mutate(groups = np.array(['Baseline']*2 +
                                                ['Core effects']*6 + 
                                                ['Demographics']*6 +
                                                ['Fit statistics']*6
                                                )
                              )
tab_rows_grouped.print()

```

``` python
shape: (20, 6)
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                        Model Linear    Model Linear   Model Logit     Model Logit    groups         │
│ str                    Adjusted: Yes   Adjusted: No   Adjusted: Yes   Adjusted: No   str            │
│                        str             str            str             str                           │
╞═════════════════════════════════════════════════════════════════════════════════════════════════════╡
│ Intercept              -0.1194         -0.1194        -0.1600         -0.1600        Baseline       │
│                        (0.1030)        (0.1030)       (0.1588)        (0.1588)       Baseline       │
│ treatment              -0.5137***      -0.5137***     -0.4336***      -0.4336***     Core effects   │
│                        (0.0609)        (0.0609)       (0.0918)        (0.0918)       Core effects   │
│ ideology               -0.1021***      -0.1021***     -0.0805*        -0.0805*       Core effects   │
│                        (0.0074)        (0.0074)       (0.0314)        (0.0314)       Core effects   │
│ treatment x ideology   -0.2804***      -0.2804***     -0.2886***      -0.2886***     Core effects   │
│                        (0.0104)        (0.0104)       (0.0427)        (0.0427)       Core effects   │
│ Income (std)           0.0348          0.0348         -0.0467         -0.0467        Demographics   │
│                        (0.0307)        (0.0307)       (0.0639)        (0.0639)       Demographics   │
│ age                    0.0234***       0.0234***      0.0200***       0.0200***      Demographics   │
│                        (0.0020)        (0.0020)       (0.0050)        (0.0050)       Demographics   │
│ gender                 -0.5098***      -0.5098***     -0.1203         -0.1203        Demographics   │
│                        (0.0610)        (0.0610)       (0.1244)        (0.1244)       Demographics   │
│ N. Obs.                1017            1017           1017            1017           Fit statistics │
│ R2 (adj)               0.7641          0.7641                                        Fit statistics │
│ R2 (pseudo)                                           0.2843          0.2843         Fit statistics │
│ BIC                    2859.2311       2859.2311      -5968.2760      -5968.2760     Fit statistics │
│ AIC                    2824.7588       2824.7588      1039.5825       1039.5825      Fit statistics │
│ Std. Error             Classical       Classical      Clustered       Clustered      Fit statistics │
└─────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

Then, we apply the `to_latex()` function:

``` {.python exports="both" results="output code latex" tangle="src-regression-table.py" cache="yes" hlines="yes" colnames="yes" noweb="no" session="*Python*"}

tabl = tab_rows_grouped.to_latex(group_rows_by='groups')
print(tabl)

```

```{=latex}
\begin{table}[!htb]
\centering
\resizebox{\ifdim\width>\linewidth\linewidth\else\width\fi}{!}{
\begin{tabular}{lllll}
\toprule
  & \makecell{Model Linear\\Adjusted: Yes} & \makecell{Model Linear\\Adjusted: No} & \makecell{Model Logit\\Adjusted: Yes} & \makecell{Model Logit\\Adjusted: No}\\
\midrule
\addlinespace[0.3em]\multicolumn{5}{l}{ \textbf{Baseline} }\\
\hspace{1em}Intercept  &  -0.1194   &  -0.1194   &  -0.1600   &  -0.1600  \\
\hspace{1em}  &  (0.1030)  &  (0.1030)  &  (0.1588)  &  (0.1588) \\
\addlinespace[0.3em]\multicolumn{5}{l}{ \textbf{Core effects} }\\
\hspace{1em}treatment  &  -0.5137***  &  -0.5137***  &  -0.4336***  &  -0.4336*** \\
\hspace{1em}  &  (0.0609)  &  (0.0609)  &  (0.0918)  &  (0.0918) \\
\hspace{1em}ideology  &  -0.1021***  &  -0.1021***  &  -0.0805*  &  -0.0805* \\
\hspace{1em}  &  (0.0074)  &  (0.0074)  &  (0.0314)  &  (0.0314) \\
\hspace{1em}treatment x ideology  &  -0.2804***  &  -0.2804***  &  -0.2886***  &  -0.2886*** \\
\hspace{1em}  &  (0.0104)  &  (0.0104)  &  (0.0427)  &  (0.0427) \\
\addlinespace[0.3em]\multicolumn{5}{l}{ \textbf{Demographics} }\\
\hspace{1em}Income (std)  &  0.0348   &  0.0348   &  -0.0467   &  -0.0467  \\
\hspace{1em}  &  (0.0307)  &  (0.0307)  &  (0.0639)  &  (0.0639) \\
\hspace{1em}age  &  0.0234***  &  0.0234***  &  0.0200***  &  0.0200*** \\
\hspace{1em}  &  (0.0020)  &  (0.0020)  &  (0.0050)  &  (0.0050) \\
\hspace{1em}gender  &  -0.5098***  &  -0.5098***  &  -0.1203   &  -0.1203  \\
\hspace{1em}  &  (0.0610)  &  (0.0610)  &  (0.1244)  &  (0.1244) \\
\addlinespace[0.3em]\multicolumn{5}{l}{ \textbf{Fit statistics} }\\
\hspace{1em}N. Obs.  &  1017  &  1017  &  1017  &  1017 \\
\hspace{1em}R2 (adj)  &  0.7641  &  0.7641  &    &   \\
\hspace{1em}R2 (pseudo)  &    &    &  0.2843  &  0.2843 \\
\hspace{1em}BIC  &  2859.2311  &  2859.2311  &  -5968.2760  &  -5968.2760 \\
\hspace{1em}AIC  &  2824.7588  &  2824.7588  &  1039.5825  &  1039.5825 \\
\hspace{1em}Std. Error  &  Classical  &  Classical  &  Clustered  &  Clustered \\
\bottomrule
\end{tabular}}
\end{table}
```
### Grouping columns

We can also group columns instead, producing something like this:

![](./tables-and-figures/regression-table-latex-1-grouped-cols.png)

We need to post-process the `tibble` outcome from the `models2tab()`
function using tidypolars$^{4sci} $ function `to_latex()`. The code:

``` {.python exports="both" results="output code latex" tangle="src-regression-table.py" cache="yes" hlines="yes" colnames="yes" noweb="no" session="*Python*"}
caption = "A regression table"
label = 'tab-regression'
header = [('', ''),
          ('Linear Models', 'Adjusted: Yes'),
          ('Linear Models', 'Adjusted: No'),
          ('Logit Models', 'Adjusted: Yes'),
          ('Logit Models', 'Adjusted: No'),
          ]
tabl = tab.to_latex(caption = caption,
                    label = label,
                    header = header,
                    align = 'lcccc',
                    footnotes = None)
print(tabl)

```

```{=latex}
\begin{table}[!htb]
\caption{A regression table}
\label{tab-regression}
\centering
\resizebox{\ifdim\width>\linewidth\linewidth\else\width\fi}{!}{
\begin{tabular}{lcccc}
\toprule
  &  \multicolumn{2}{c}{Linear Models}  &  \multicolumn{2}{c}{Logit Models} \\
\cmidrule(lr){2-3} \cmidrule(lr){4-5}
  &  Adjusted: Yes  &  Adjusted: No  &  Adjusted: Yes  &  Adjusted: No \\
\midrule
Intercept  &  -0.1194   &  -0.1194   &  -0.1600   &  -0.1600  \\
  &  (0.1030)  &  (0.1030)  &  (0.1588)  &  (0.1588) \\
treatment  &  -0.5137***  &  -0.5137***  &  -0.4336***  &  -0.4336*** \\
  &  (0.0609)  &  (0.0609)  &  (0.0918)  &  (0.0918) \\
ideology  &  -0.1021***  &  -0.1021***  &  -0.0805*  &  -0.0805* \\
  &  (0.0074)  &  (0.0074)  &  (0.0314)  &  (0.0314) \\
treatment x ideology  &  -0.2804***  &  -0.2804***  &  -0.2886***  &  -0.2886*** \\
  &  (0.0104)  &  (0.0104)  &  (0.0427)  &  (0.0427) \\
Income (std)  &  0.0348   &  0.0348   &  -0.0467   &  -0.0467  \\
  &  (0.0307)  &  (0.0307)  &  (0.0639)  &  (0.0639) \\
age  &  0.0234***  &  0.0234***  &  0.0200***  &  0.0200*** \\
  &  (0.0020)  &  (0.0020)  &  (0.0050)  &  (0.0050) \\
gender  &  -0.5098***  &  -0.5098***  &  -0.1203   &  -0.1203  \\
  &  (0.0610)  &  (0.0610)  &  (0.1244)  &  (0.1244) \\
N. Obs.  &  1017  &  1017  &  1017  &  1017 \\
R2 (adj)  &  0.7641  &  0.7641  &    &   \\
R2 (pseudo)  &    &    &  0.2843  &  0.2843 \\
BIC  &  2859.2311  &  2859.2311  &  -5968.2760  &  -5968.2760 \\
AIC  &  2824.7588  &  2824.7588  &  1039.5825  &  1039.5825 \\
Std. Error  &  Classical  &  Classical  &  Clustered  &  Clustered \\
\bottomrule
\end{tabular}}
\end{table}
```
### Plotting coefficients

The tidy format facilitates plotting the model coefficients. One can use
the `unnest()` function. Here is the code:

``` {.python exports="both" results="output code" tangle="src-regression-table.py" cache="yes" hlines="yes" colnames="yes" noweb="no" session="*Python*"}
model = 'Linear'
adjusted = 'Yes'
tab = (res
       .filter(tp.col("model")==model)
       .filter(tp.col("adjusted")==adjusted)
       .select('partisanship', 'summ')
       .unnest('summ')
       #
       .filter(~tp.col("term").str.contains('Intercept'))
       )
tab.print()
```

``` python
shape: (12, 8)
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ partisanship   term                 Coef.   Std.Err.        t   P>|t|   [0.025   0.975] │
│ str            str                    f64        f64      f64     f64      f64      f64 │
╞═════════════════════════════════════════════════════════════════════════════════════════╡
│ republican     treatment            -0.55       0.07    -8.35    0.00    -0.67    -0.42 │
│ republican     ideology             -0.12       0.01   -14.41    0.00    -0.13    -0.10 │
│ republican     treatment:ideology   -0.29       0.01   -25.66    0.00    -0.31    -0.27 │
│ republican     income               -0.01       0.03    -0.25    0.81    -0.07     0.06 │
│ republican     age                   0.02       0.00     7.81    0.00     0.01     0.02 │
│ republican     gender               -0.44       0.07    -6.76    0.00    -0.57    -0.31 │
│ democrat       treatment            -0.51       0.06    -8.44    0.00    -0.63    -0.39 │
│ democrat       ideology             -0.10       0.01   -13.86    0.00    -0.12    -0.09 │
│ democrat       treatment:ideology   -0.28       0.01   -27.00    0.00    -0.30    -0.26 │
│ democrat       income                0.03       0.03     1.13    0.26    -0.03     0.10 │
│ democrat       age                   0.02       0.00    11.58    0.00     0.02     0.03 │
│ democrat       gender               -0.51       0.06    -8.36    0.00    -0.63    -0.39 │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

Here is an example of a possible plot using
[Altair](https://altair-viz.github.io/):

``` vegalite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.20.1.json",
  "config": {
    "view": {
      "continuousHeight": 300,
      "continuousWidth": 300
    }
  },
  "data": {
    "name": "data-f99985beb9b1bd22f3c5069d5033afdc"
  },
  "datasets": {
    "data-f99985beb9b1bd22f3c5069d5033afdc": [
      {
        "Coef.": -0.5453875271227993,
        "P>|t|": 2.325085825422768e-16,
        "Std.Err.": 0.0653182412692631,
        "hi": -0.41720717008879227,
        "lo": -0.6735678841568062,
        "partisanship": "republican",
        "t": -8.34969706049699,
        "term": "treatment"
      },
      {
        "Coef.": -0.11672998920234258,
        "P>|t|": 8.055899574345312e-43,
        "Std.Err.": 0.008101084204688823,
        "hi": -0.10083244135749256,
        "lo": -0.1326275370471926,
        "partisanship": "republican",
        "t": -14.40918107415554,
        "term": "ideology"
      },
      {
        "Coef.": -0.28807694912332255,
        "P>|t|": 2.272577821261762e-111,
        "Std.Err.": 0.011228310093157067,
        "hi": -0.2660425408376438,
        "lo": -0.3101113574090013,
        "partisanship": "republican",
        "t": -25.656305065789635,
        "term": "treatment:ideology"
      },
      {
        "Coef.": -0.008017956121100761,
        "P>|t|": 0.8064667941681202,
        "Std.Err.": 0.03271925395417075,
        "hi": 0.05619022787520521,
        "lo": -0.07222614011740673,
        "partisanship": "republican",
        "t": -0.24505314614848378,
        "term": "income"
      },
      {
        "Coef.": 0.016927139267716683,
        "P>|t|": 1.4553886048999363e-14,
        "Std.Err.": 0.0021669566636691516,
        "hi": 0.021179569728624375,
        "lo": 0.012674708806808991,
        "partisanship": "republican",
        "t": 7.8114802900835025,
        "term": "age"
      },
      {
        "Coef.": -0.4402524009430397,
        "P>|t|": 2.305992236730476e-11,
        "Std.Err.": 0.06508529343308622,
        "hi": -0.3125291801734395,
        "lo": -0.5679756217126399,
        "partisanship": "republican",
        "t": -6.76423778277439,
        "term": "gender"
      },
      {
        "Coef.": -0.5137398145136601,
        "P>|t|": 1.1192712446663049e-16,
        "Std.Err.": 0.06089376892077548,
        "hi": -0.3942470256354935,
        "lo": -0.6332326033918267,
        "partisanship": "democrat",
        "t": -8.436656551543889,
        "term": "treatment"
      },
      {
        "Coef.": -0.10214590800016095,
        "P>|t|": 3.927130599200094e-40,
        "Std.Err.": 0.007368376775750375,
        "hi": -0.08768682776840457,
        "lo": -0.11660498823191733,
        "partisanship": "democrat",
        "t": -13.86274224417069,
        "term": "ideology"
      },
      {
        "Coef.": -0.28039095958730786,
        "P>|t|": 2.7074723158659304e-121,
        "Std.Err.": 0.01038562273952341,
        "hi": -0.2600110907209754,
        "lo": -0.30077082845364034,
        "partisanship": "democrat",
        "t": -26.997991995246963,
        "term": "treatment:ideology"
      },
      {
        "Coef.": 0.03480719155804167,
        "P>|t|": 0.25698551718272933,
        "Std.Err.": 0.030689129988868705,
        "hi": 0.09502894816150531,
        "lo": -0.025414565045421965,
        "partisanship": "democrat",
        "t": 1.1341863249517543,
        "term": "income"
      },
      {
        "Coef.": 0.023373717983439,
        "P>|t|": 3.485716259235037e-29,
        "Std.Err.": 0.0020192981495198376,
        "hi": 0.027336218116688654,
        "lo": 0.019411217850189344,
        "partisanship": "democrat",
        "t": 11.575169317615114,
        "term": "age"
      },
      {
        "Coef.": -0.509783493509636,
        "P>|t|": 2.0683016060635783e-16,
        "Std.Err.": 0.06098256476278831,
        "hi": -0.39011645917103976,
        "lo": -0.6294505278482323,
        "partisanship": "democrat",
        "t": -8.35949579183175,
        "term": "gender"
      }
    ]
  },
  "height": 450,
  "layer": [
    {
      "encoding": {
        "color": {
          "field": "partisanship",
          "type": "nominal"
        },
        "fill": {
          "field": "partisanship",
          "type": "nominal"
        },
        "x": {
          "field": "lo",
          "title": "Estimate",
          "type": "quantitative"
        },
        "x2": {
          "field": "hi"
        },
        "y": {
          "field": "term",
          "title": "Variables",
          "type": "nominal"
        },
        "yOffset": {
          "field": "partisanship",
          "type": "nominal"
        }
      },
      "mark": {
        "thickness": 1.2,
        "type": "errorbar"
      },
      "name": "view_21"
    },
    {
      "encoding": {
        "color": {
          "field": "partisanship",
          "type": "nominal"
        },
        "fill": {
          "field": "partisanship",
          "title": "Partisanship",
          "type": "nominal"
        },
        "x": {
          "field": "Coef\\.",
          "title": "Estimate",
          "type": "quantitative"
        },
        "y": {
          "field": "term",
          "scale": {
            "padding": 0.6
          },
          "title": "Variables",
          "type": "nominal"
        },
        "yOffset": {
          "field": "partisanship",
          "type": "nominal"
        }
      },
      "mark": {
        "type": "point"
      }
    }
  ],
  "params": [
    {
      "bind": "scales",
      "name": "param_20",
      "select": {
        "encodings": [
          "x",
          "y"
        ],
        "type": "interval"
      },
      "views": [
        "view_21"
      ]
    }
  ],
  "width": 600
}
```

### Plotting fitted line

The tidy format facilitates plotting the model prediction or fitted
values. One can use the `unnest()` function. Here is the code:

``` {.python exports="both" results="output code" tangle="src-regression-table.py" cache="yes" hlines="yes" colnames="yes" noweb="no" session="*Python*"}
model = 'Linear'
adjusted = 'Yes'
tab = (res
       .filter(tp.col("model")==model)
       .filter(tp.col("adjusted")==adjusted)
       .select('partisanship', "pred")
       .unnest("pred")
       )
tab.head().print()
```

``` python
shape: (5, 15)
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ partisanship     age   income   gender   ideology   treatment   group   vote_conservative   rate_conservative   mean   mean_se   mean_ci_lower   mean_ci_upper   obs_ci_lower   obs_ci_upper │
│ str              f64      f64      f64        i64         i64   str                   f64                 f64    f64       f64             f64             f64            f64            f64 │
╞══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╡
│ republican     43.92    -0.04     0.49        -10           0   a                    0.59                0.46   1.81      0.09            1.64            1.98          -0.19           3.82 │
│ republican     43.92    -0.04     0.49         -9           0   a                    0.59                0.46   1.70      0.08            1.54            1.85          -0.31           3.70 │
│ republican     43.92    -0.04     0.49         -8           0   a                    0.59                0.46   1.58      0.07            1.43            1.73          -0.42           3.58 │
│ republican     43.92    -0.04     0.49         -7           0   a                    0.59                0.46   1.46      0.07            1.33            1.60          -0.54           3.46 │
│ republican     43.92    -0.04     0.49         -6           0   a                    0.59                0.46   1.35      0.06            1.22            1.47          -0.66           3.35 │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

The plot with predicted values:

``` vegalite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.20.1.json",
  "columns": 2,
  "config": {
    "view": {
      "continuousHeight": 300,
      "continuousWidth": 300
    }
  },
  "data": {
    "name": "data-30a612b71a3f202810f71efbf3c941e1"
  },
  "datasets": {
    "data-30a612b71a3f202810f71efbf3c941e1": [
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": -10,
        "income": -0.03684137270467414,
        "mean": 1.8128005685567476,
        "mean_ci_lower": 1.6406086589712454,
        "mean_ci_upper": 1.9849924781422499,
        "mean_se": 0.08774568081392536,
        "obs_ci_lower": -0.19202807366847408,
        "obs_ci_upper": 3.8176292107819694,
        "rate_conservative": 0.45688877688284546,
        "treatment": 0,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": -9,
        "income": -0.03684137270467414,
        "mean": 1.696070579354405,
        "mean_ci_lower": 1.5371802277454272,
        "mean_ci_upper": 1.854960930963383,
        "mean_se": 0.08096746304895855,
        "obs_ci_lower": -0.30765943609037727,
        "obs_ci_upper": 3.6998005947991874,
        "rate_conservative": 0.45688877688284546,
        "treatment": 0,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": -8,
        "income": -0.03684137270467414,
        "mean": 1.5793405901520623,
        "mean_ci_lower": 1.433232075694122,
        "mean_ci_upper": 1.7254491046100027,
        "mean_se": 0.07445408500715446,
        "obs_ci_lower": -0.42341639184975555,
        "obs_ci_upper": 3.58209757215388,
        "rate_conservative": 0.45688877688284546,
        "treatment": 0,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": -7,
        "income": -0.03684137270467414,
        "mean": 1.4626106009497197,
        "mean_ci_lower": 1.3286153912788279,
        "mean_ci_upper": 1.5966058106206116,
        "mean_se": 0.06828137818251484,
        "obs_ci_lower": -0.5392991240815241,
        "obs_ci_upper": 3.4645203259809634,
        "rate_conservative": 0.45688877688284546,
        "treatment": 0,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": -6,
        "income": -0.03684137270467414,
        "mean": 1.3458806117473772,
        "mean_ci_lower": 1.2231320944962716,
        "mean_ci_upper": 1.4686291289984827,
        "mean_se": 0.062550280329808,
        "obs_ci_lower": -0.6553077925382536,
        "obs_ci_upper": 3.347069016033008,
        "rate_conservative": 0.45688877688284546,
        "treatment": 0,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": -5,
        "income": -0.03684137270467414,
        "mean": 1.2291506225450346,
        "mean_ci_lower": 1.116522274359943,
        "mean_ci_upper": 1.3417789707301262,
        "mean_se": 0.057393237082032894,
        "obs_ci_lower": -0.7714425334401664,
        "obs_ci_upper": 3.229743778530236,
        "rate_conservative": 0.45688877688284546,
        "treatment": 0,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": -4,
        "income": -0.03684137270467414,
        "mean": 1.112420633342692,
        "mean_ci_lower": 1.0084564318240055,
        "mean_ci_upper": 1.2163848348613786,
        "mean_se": 0.05297815480699775,
        "obs_ci_lower": -0.8877034593468947,
        "obs_ci_upper": 3.1125447260322785,
        "rate_conservative": 0.45688877688284546,
        "treatment": 0,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": -3,
        "income": -0.03684137270467414,
        "mean": 0.9956906441403495,
        "mean_ci_lower": 0.8985442101610595,
        "mean_ci_upper": 1.0928370781196395,
        "mean_se": 0.04950395177495351,
        "obs_ci_lower": -1.0040906590512813,
        "obs_ci_upper": 2.99547194733198,
        "rate_conservative": 0.45688877688284546,
        "treatment": 0,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": -2,
        "income": -0.03684137270467414,
        "mean": 0.8789606549380069,
        "mean_ci_lower": 0.7863768111674785,
        "mean_ci_upper": 0.9715444987085353,
        "mean_se": 0.04717894367726501,
        "obs_ci_lower": -1.1206041974954541,
        "obs_ci_upper": 2.878525507371468,
        "rate_conservative": 0.45688877688284546,
        "treatment": 0,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": -1,
        "income": -0.03684137270467414,
        "mean": 0.7622306657356643,
        "mean_ci_lower": 0.6716129485126111,
        "mean_ci_upper": 0.8528483829587176,
        "mean_se": 0.046177043455066284,
        "obs_ci_lower": -1.2372441157093634,
        "obs_ci_upper": 2.761705447180692,
        "rate_conservative": 0.45688877688284546,
        "treatment": 0,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": 0,
        "income": -0.03684137270467414,
        "mean": 0.6455006765333217,
        "mean_ci_lower": 0.5540849378606648,
        "mean_ci_upper": 0.7369164152059785,
        "mean_se": 0.04658369981637929,
        "obs_ci_lower": -1.3540104307719094,
        "obs_ci_upper": 2.645011783838553,
        "rate_conservative": 0.45688877688284546,
        "treatment": 0,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": 1,
        "income": -0.03684137270467414,
        "mean": 0.5287706873309791,
        "mean_ci_lower": 0.4338624793910105,
        "mean_ci_upper": 0.6236788952709477,
        "mean_se": 0.04836339489217966,
        "obs_ci_lower": -1.470903135794758,
        "obs_ci_upper": 2.528444510456716,
        "rate_conservative": 0.45688877688284546,
        "treatment": 0,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": 2,
        "income": -0.03684137270467414,
        "mean": 0.41204069812863653,
        "mean_ci_lower": 0.3112252099998588,
        "mean_ci_upper": 0.5128561862574142,
        "mean_se": 0.05137363110579394,
        "obs_ci_lower": -1.5879221999288666,
        "obs_ci_upper": 2.4120035961861395,
        "rate_conservative": 0.45688877688284546,
        "treatment": 0,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": 3,
        "income": -0.03684137270467414,
        "mean": 0.29531070892629396,
        "mean_ci_lower": 0.1865659554258619,
        "mean_ci_upper": 0.404055462426726,
        "mean_se": 0.05541423202638838,
        "obs_ci_lower": -1.7050675683937215,
        "obs_ci_upper": 2.2956889862463092,
        "rate_conservative": 0.45688877688284546,
        "treatment": 0,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": 4,
        "income": -0.03684137270467414,
        "mean": 0.1785807197239514,
        "mean_ci_lower": 0.06029063461089412,
        "mean_ci_upper": 0.2968708048370087,
        "mean_se": 0.06027834917893433,
        "obs_ci_lower": -1.8223391625292034,
        "obs_ci_upper": 2.179500601977106,
        "rate_conservative": 0.45688877688284546,
        "treatment": 0,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": 5,
        "income": -0.03684137270467414,
        "mean": 0.06185073052160878,
        "mean_ci_lower": -0.06724276704196924,
        "mean_ci_upper": 0.1909442280851868,
        "mean_se": 0.0657835600966045,
        "obs_ci_lower": -1.939736879869983,
        "obs_ci_upper": 2.0634383409132004,
        "rate_conservative": 0.45688877688284546,
        "treatment": 0,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": 6,
        "income": -0.03684137270467414,
        "mean": -0.054879258680733844,
        "mean_ci_lower": -0.1957450886229143,
        "mean_ci_upper": 0.0859865712614466,
        "mean_se": 0.07178251394881997,
        "obs_ci_lower": -2.0572605942422753,
        "obs_ci_upper": 1.9475020768808076,
        "rate_conservative": 0.45688877688284546,
        "treatment": 0,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": 7,
        "income": -0.03684137270467414,
        "mean": -0.1716092478830764,
        "mean_ci_lower": -0.3249933964524761,
        "mean_ci_upper": -0.018225099313676718,
        "mean_se": 0.07816160802609176,
        "obs_ci_lower": -2.1749101558827415,
        "obs_ci_upper": 1.8316916601165887,
        "rate_conservative": 0.45688877688284546,
        "treatment": 0,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": 8,
        "income": -0.03684137270467414,
        "mean": -0.288339237085419,
        "mean_ci_lower": -0.4548194943965448,
        "mean_ci_upper": -0.12185897977429319,
        "mean_se": 0.08483513281783207,
        "obs_ci_lower": -2.2926853915792735,
        "obs_ci_upper": 1.7160069174084356,
        "rate_conservative": 0.45688877688284546,
        "treatment": 0,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": 9,
        "income": -0.03684137270467414,
        "mean": -0.40506922628776165,
        "mean_ci_lower": -0.5850973329026905,
        "mean_ci_upper": -0.22504111967283277,
        "mean_se": 0.09173885589975994,
        "obs_ci_lower": -2.41058610483336,
        "obs_ci_upper": 1.600447652257837,
        "rate_conservative": 0.45688877688284546,
        "treatment": 0,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": -10,
        "income": -0.03684137270467414,
        "mean": 4.148182532667174,
        "mean_ci_lower": 3.97405325632586,
        "mean_ci_upper": 4.322311809008487,
        "mean_se": 0.08873292560018821,
        "obs_ci_lower": 2.14318656363405,
        "obs_ci_upper": 6.153178501700298,
        "rate_conservative": 0.45688877688284546,
        "treatment": 1,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": -9,
        "income": -0.03684137270467414,
        "mean": 3.743375594341509,
        "mean_ci_lower": 3.582097924514253,
        "mean_ci_upper": 3.904653264168765,
        "mean_se": 0.08218399443470457,
        "obs_ci_lower": 1.739454857948766,
        "obs_ci_upper": 5.747296330734251,
        "rate_conservative": 0.45688877688284546,
        "treatment": 1,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": -8,
        "income": -0.03684137270467414,
        "mean": 3.3385686560158434,
        "mean_ci_lower": 3.189695652472127,
        "mean_ci_upper": 3.48744165955956,
        "mean_se": 0.07586281540289729,
        "obs_ci_lower": 1.335608096707685,
        "obs_ci_upper": 5.341529215324002,
        "rate_conservative": 0.45688877688284546,
        "treatment": 1,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": -7,
        "income": -0.03684137270467414,
        "mean": 2.9337617176901785,
        "mean_ci_lower": 2.796725014297243,
        "mean_ci_upper": 3.070798421083114,
        "mean_se": 0.06983126480595979,
        "obs_ci_lower": 0.9316461143753432,
        "obs_ci_upper": 4.935877321005014,
        "rate_conservative": 0.45688877688284546,
        "treatment": 1,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": -6,
        "income": -0.03684137270467414,
        "mean": 2.528954779364513,
        "mean_ci_lower": 2.403025642692584,
        "mean_ci_upper": 2.654883916036442,
        "mean_se": 0.06417106272987524,
        "obs_ci_lower": 0.5275687650177403,
        "obs_ci_upper": 4.530340793711286,
        "rate_conservative": 0.45688877688284546,
        "treatment": 1,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": -5,
        "income": -0.03684137270467414,
        "mean": 2.124147841038848,
        "mean_ci_lower": 2.0083875743558046,
        "mean_ci_upper": 2.2399081077218916,
        "mean_se": 0.05898920242975475,
        "obs_ci_lower": 0.12337592242782014,
        "obs_ci_upper": 4.124919759649876,
        "rate_conservative": 0.45688877688284546,
        "treatment": 1,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": -4,
        "income": -0.03684137270467414,
        "mean": 1.719340902713183,
        "mean_ci_lower": 1.6125423366386362,
        "mean_ci_upper": 1.8261394687877297,
        "mean_se": 0.054422492396536536,
        "obs_ci_lower": -0.2809325197657302,
        "obs_ci_upper": 3.7196143251920963,
        "rate_conservative": 0.45688877688284546,
        "treatment": 1,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": -3,
        "income": -0.03684137270467414,
        "mean": 1.3145339643875178,
        "mean_ci_lower": 1.2151627885763836,
        "mean_ci_upper": 1.413905140198652,
        "mean_se": 0.050637637365294474,
        "obs_ci_lower": -0.6853566480065729,
        "obs_ci_upper": 3.3144245767816085,
        "rate_conservative": 0.45688877688284546,
        "treatment": 1,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": -2,
        "income": -0.03684137270467414,
        "mean": 0.9097270260618526,
        "mean_ci_lower": 0.8158839126115129,
        "mean_ci_upper": 1.0035701395121923,
        "mean_se": 0.047820643253333114,
        "obs_ci_lower": -1.089896528735894,
        "obs_ci_upper": 2.9093505808595994,
        "rate_conservative": 0.45688877688284546,
        "treatment": 1,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": -1,
        "income": -0.03684137270467414,
        "mean": 0.5049200877361876,
        "mean_ci_lower": 0.41435722671977915,
        "mean_ci_upper": 0.595482948752596,
        "mean_se": 0.04614908978865706,
        "obs_ci_lower": -1.4945522083348033,
        "obs_ci_upper": 2.5043923838071787,
        "rate_conservative": 0.45688877688284546,
        "treatment": 1,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": 0,
        "income": -0.03684137270467414,
        "mean": 0.10011314941052246,
        "mean_ci_lower": 0.01033600230526345,
        "mean_ci_upper": 0.1898902965157815,
        "mean_se": 0.04574870511190462,
        "obs_ci_lower": -1.8993237130840859,
        "obs_ci_upper": 2.099550011905131,
        "rate_conservative": 0.45688877688284546,
        "treatment": 1,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": 1,
        "income": -0.03684137270467414,
        "mean": -0.30469378891514276,
        "mean_ci_lower": -0.39624401001099446,
        "mean_ci_upper": -0.21314356781929106,
        "mean_se": 0.04665222946919021,
        "obs_ci_lower": -2.3042110491413763,
        "obs_ci_upper": 1.694823471311091,
        "rate_conservative": 0.45688877688284546,
        "treatment": 1,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": 2,
        "income": -0.03684137270467414,
        "mean": -0.7095007272408076,
        "mean_ci_lower": -0.8052407518726058,
        "mean_ci_upper": -0.6137607026090094,
        "mean_se": 0.048787272658055415,
        "obs_ci_lower": -2.7092142025358115,
        "obs_ci_upper": 1.290212748054196,
        "rate_conservative": 0.45688877688284546,
        "treatment": 1,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": 3,
        "income": -0.03684137270467414,
        "mean": -1.1143076655664728,
        "mean_ci_lower": -1.2163569876796223,
        "mean_ci_upper": -1.0122583434533232,
        "mean_se": 0.05200236914134205,
        "obs_ci_lower": -3.114333139180166,
        "obs_ci_upper": 0.8857178080472203,
        "rate_conservative": 0.45688877688284546,
        "treatment": 1,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": 4,
        "income": -0.03684137270467414,
        "mean": -1.5191146038921381,
        "mean_ci_lower": -1.6292289919822847,
        "mean_ci_upper": -1.4090002158019916,
        "mean_se": 0.05611217143498244,
        "obs_ci_lower": -3.5195678049004475,
        "obs_ci_upper": 0.4813385971161712,
        "rate_conservative": 0.45688877688284546,
        "treatment": 1,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": 5,
        "income": -0.03684137270467414,
        "mean": -1.923921542217803,
        "mean_ci_lower": -2.0435020392841703,
        "mean_ci_upper": -1.8043410451514361,
        "mean_se": 0.0609359182577961,
        "obs_ci_lower": -3.924918125482893,
        "obs_ci_upper": 0.07707504104728669,
        "rate_conservative": 0.45688877688284546,
        "treatment": 1,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": 6,
        "income": -0.03684137270467414,
        "mean": -2.3287284805434685,
        "mean_ci_lower": -2.4588707664703318,
        "mean_ci_upper": -2.198586194616605,
        "mean_se": 0.06631800244751235,
        "obs_ci_lower": -4.330384006738272,
        "obs_ci_upper": -0.32707295434866523,
        "rate_conservative": 0.45688877688284546,
        "treatment": 1,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": 7,
        "income": -0.03684137270467414,
        "mean": -2.7335354188691334,
        "mean_ci_lower": -2.875090130508688,
        "mean_ci_upper": -2.591980707229579,
        "mean_se": 0.07213355479436179,
        "obs_ci_lower": -4.7359653345833586,
        "obs_ci_upper": -0.7311055031549079,
        "rate_conservative": 0.45688877688284546,
        "treatment": 1,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": 8,
        "income": -0.03684137270467414,
        "mean": -3.1383423571947984,
        "mean_ci_lower": -3.291970677116301,
        "mean_ci_upper": -2.984714037273296,
        "mean_se": 0.07828603304453247,
        "obs_ci_lower": -5.141661975139431,
        "obs_ci_upper": -1.1350227392501662,
        "rate_conservative": 0.45688877688284546,
        "treatment": 1,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Republican",
        "age": 43.92268565615463,
        "gender": 0.4872838250254323,
        "group": "a",
        "ideology": 9,
        "income": -0.03684137270467414,
        "mean": -3.5431492955204638,
        "mean_ci_lower": -3.709368390301742,
        "mean_ci_upper": -3.3769302007391855,
        "mean_se": 0.08470204942245235,
        "obs_ci_lower": -5.547473774847559,
        "obs_ci_upper": -1.5388248161933684,
        "rate_conservative": 0.45688877688284546,
        "treatment": 1,
        "vote_conservative": 0.5879959308240081
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": -10,
        "income": 0.003231334765282966,
        "mean": 1.672110275322947,
        "mean_ci_lower": 1.5034558410540115,
        "mean_ci_upper": 1.8407647095918827,
        "mean_se": 0.08594664367828797,
        "obs_ci_lower": -0.23285150413147848,
        "obs_ci_upper": 3.5770720547773727,
        "rate_conservative": 0.4955641780029095,
        "treatment": 0,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": -9,
        "income": 0.003231334765282966,
        "mean": 1.569964367322786,
        "mean_ci_lower": 1.4136509322606192,
        "mean_ci_upper": 1.726277802384953,
        "mean_se": 0.07965764531274938,
        "obs_ci_lower": -0.333944494194627,
        "obs_ci_upper": 3.4738732288401994,
        "rate_conservative": 0.4955641780029095,
        "treatment": 0,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": -8,
        "income": 0.003231334765282966,
        "mean": 1.4678184593226251,
        "mean_ci_lower": 1.3234522868112275,
        "mean_ci_upper": 1.6121846318340227,
        "mean_se": 0.0735692959501435,
        "obs_ci_lower": -0.43514676756650217,
        "obs_ci_upper": 3.3707836862117526,
        "rate_conservative": 0.4955641780029095,
        "treatment": 0,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": -7,
        "income": 0.003231334765282966,
        "mean": 1.3656725513224641,
        "mean_ci_lower": 1.2327536905368568,
        "mean_ci_upper": 1.4985914121080715,
        "mean_se": 0.06773572254760893,
        "obs_ci_lower": -0.5364584868912918,
        "obs_ci_upper": 3.26780358953622,
        "rate_conservative": 0.4955641780029095,
        "treatment": 0,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": -6,
        "income": 0.003231334765282966,
        "mean": 1.2635266433223034,
        "mean_ci_lower": 1.141414459893321,
        "mean_ci_upper": 1.3856388267512858,
        "mean_se": 0.06222861772619046,
        "obs_ci_lower": -0.6378797962180152,
        "obs_ci_upper": 3.164933082862622,
        "rate_conservative": 0.4955641780029095,
        "treatment": 0,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": -5,
        "income": 0.003231334765282966,
        "mean": 1.1613807353221424,
        "mean_ci_lower": 1.04924921819453,
        "mean_ci_upper": 1.2735122524497546,
        "mean_se": 0.057142449823199486,
        "obs_ci_lower": -0.7394108208767318,
        "obs_ci_upper": 3.0621722915210166,
        "rate_conservative": 0.4955641780029095,
        "treatment": 0,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": -4,
        "income": 0.003231334765282966,
        "mean": 1.0592348273219814,
        "mean_ci_lower": 0.9560180703142973,
        "mean_ci_upper": 1.1624515843296654,
        "mean_se": 0.052599469884213004,
        "obs_ci_lower": -0.8410516673705375,
        "obs_ci_upper": 2.9595213220145,
        "rate_conservative": 0.4955641780029095,
        "treatment": 0,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": -3,
        "income": 0.003231334765282966,
        "mean": 0.9570889193218205,
        "mean_ci_lower": 0.8614225682712902,
        "mean_ci_upper": 1.0527552703723508,
        "mean_se": 0.04875176760921007,
        "obs_ci_lower": -0.942802423283572,
        "obs_ci_upper": 2.856980261927213,
        "rate_conservative": 0.4955641780029095,
        "treatment": 0,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": -2,
        "income": 0.003231334765282966,
        "mean": 0.8549430113216595,
        "mean_ci_lower": 0.7651180007635747,
        "mean_ci_upper": 0.9447680218797443,
        "mean_se": 0.04577500858070323,
        "obs_ci_lower": -1.0446631572052163,
        "obs_ci_upper": 2.7545491798485355,
        "rate_conservative": 0.4955641780029095,
        "treatment": 0,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": -1,
        "income": 0.003231334765282966,
        "mean": 0.7527971033214986,
        "mean_ci_lower": 0.6667555765888009,
        "mean_ci_upper": 0.8388386300541963,
        "mean_se": 0.043846937506778254,
        "obs_ci_lower": -1.1466339186706376,
        "obs_ci_upper": 2.652228125313635,
        "rate_conservative": 0.4955641780029095,
        "treatment": 0,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": 0,
        "income": 0.003231334765282966,
        "mean": 0.6506511953213376,
        "mean_ci_lower": 0.5660587244653345,
        "mean_ci_upper": 0.7352436661773408,
        "mean_se": 0.04310849567662989,
        "obs_ci_lower": -1.2487147381177985,
        "obs_ci_upper": 2.550017128760474,
        "rate_conservative": 0.4955641780029095,
        "treatment": 0,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": 1,
        "income": 0.003231334765282966,
        "mean": 0.5485052873211766,
        "mean_ci_lower": 0.4629088041524698,
        "mean_ci_upper": 0.6341017704898835,
        "mean_se": 0.04362014239889128,
        "obs_ci_lower": -1.3509056268610202,
        "obs_ci_upper": 2.4479162015033733,
        "rate_conservative": 0.4955641780029095,
        "treatment": 0,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": 2,
        "income": 0.003231334765282966,
        "mean": 0.44635937932101577,
        "mean_ci_lower": 0.3573888238631881,
        "mean_ci_upper": 0.5353299347788435,
        "mean_se": 0.04533957651893014,
        "obs_ci_lower": -1.4532065770811493,
        "obs_ci_upper": 2.3459253357231806,
        "rate_conservative": 0.4955641780029095,
        "treatment": 0,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": 3,
        "income": 0.003231334765282966,
        "mean": 0.3442134713208548,
        "mean_ci_lower": 0.2497524129507792,
        "mean_ci_upper": 0.43867452969093035,
        "mean_se": 0.04813754800102646,
        "obs_ci_lower": -1.5556175618323551,
        "obs_ci_upper": 2.2440445044740644,
        "rate_conservative": 0.4955641780029095,
        "treatment": 0,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": 4,
        "income": 0.003231334765282966,
        "mean": 0.2420675633206939,
        "mean_ci_lower": 0.1403416897161287,
        "mean_ci_upper": 0.3437934369252591,
        "mean_se": 0.05183971266129052,
        "obs_ci_lower": -1.6581385350655338,
        "obs_ci_upper": 2.1422736617069216,
        "rate_conservative": 0.4955641780029095,
        "treatment": 0,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": 5,
        "income": 0.003231334765282966,
        "mean": 0.1399216553205329,
        "mean_ci_lower": 0.029506324975848083,
        "mean_ci_upper": 0.2503369856652177,
        "mean_se": 0.05626787753841476,
        "obs_ci_lower": -1.760769431668282,
        "obs_ci_upper": 2.0406127423093476,
        "rate_conservative": 0.4955641780029095,
        "treatment": 0,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": 6,
        "income": 0.003231334765282966,
        "mean": 0.03777574732037192,
        "mean_ci_lower": -0.08244516180918222,
        "mean_ci_upper": 0.15799665644992605,
        "mean_se": 0.061264820485901615,
        "obs_ci_lower": -1.8635101675213528,
        "obs_ci_upper": 1.9390616621620966,
        "rate_conservative": 0.4955641780029095,
        "treatment": 0,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": 7,
        "income": 0.003231334765282966,
        "mean": -0.06437016067978896,
        "mean_ci_lower": -0.19526217270131715,
        "mean_ci_upper": 0.06652185134173924,
        "mean_se": 0.0667028362836266,
        "obs_ci_lower": -1.9663606395714792,
        "obs_ci_upper": 1.8376203182119015,
        "rate_conservative": 0.4955641780029095,
        "treatment": 0,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": 8,
        "income": 0.003231334765282966,
        "mean": -0.16651606867994995,
        "mean_ci_lower": -0.30875003309228005,
        "mean_ci_upper": -0.024282104267619842,
        "mean_se": 0.07248271835416821,
        "obs_ci_lower": -2.069320725920426,
        "obs_ci_upper": 1.7362885885605261,
        "rate_conservative": 0.4955641780029095,
        "treatment": 0,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": 9,
        "income": 0.003231334765282966,
        "mean": -0.26866197668011094,
        "mean_ci_lower": -0.42276068678551326,
        "mean_ci_upper": -0.11456326657470861,
        "mean_se": 0.07852901695779647,
        "obs_ci_lower": -2.17239028593008,
        "obs_ci_upper": 1.6350663325698584,
        "rate_conservative": 0.4955641780029095,
        "treatment": 0,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": -10,
        "income": 0.003231334765282966,
        "mean": 3.9622800566823657,
        "mean_ci_lower": 3.803250620376974,
        "mean_ci_upper": 4.121309492987757,
        "mean_se": 0.08104172508564757,
        "obs_ci_lower": 2.0581462839144944,
        "obs_ci_upper": 5.866413829450237,
        "rate_conservative": 0.4955641780029095,
        "treatment": 1,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": -9,
        "income": 0.003231334765282966,
        "mean": 3.579743189094897,
        "mean_ci_lower": 3.4327121724668213,
        "mean_ci_upper": 3.726774205722973,
        "mean_se": 0.07492730594701744,
        "obs_ci_lower": 1.6765739420665928,
        "obs_ci_upper": 5.482912436123201,
        "rate_conservative": 0.4955641780029095,
        "treatment": 1,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": -8,
        "income": 0.003231334765282966,
        "mean": 3.197206321507428,
        "mean_ci_lower": 3.06171587744404,
        "mean_ci_upper": 3.3326967655708155,
        "mean_se": 0.06904620663077266,
        "obs_ci_lower": 1.294893854162462,
        "obs_ci_upper": 5.099518788852394,
        "rate_conservative": 0.4955641780029095,
        "treatment": 1,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": -7,
        "income": 0.003231334765282966,
        "mean": 2.8146694539199593,
        "mean_ci_lower": 2.690134385135958,
        "mean_ci_upper": 2.9392045227039607,
        "mean_se": 0.06346332504464193,
        "obs_ci_lower": 0.9131058745620053,
        "obs_ci_upper": 4.716233033277913,
        "rate_conservative": 0.4955641780029095,
        "treatment": 1,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": -6,
        "income": 0.003231334765282966,
        "mean": 2.4321325863324907,
        "mean_ci_lower": 2.3177993513379738,
        "mean_ci_upper": 2.5464658213270077,
        "mean_se": 0.05826444973863155,
        "obs_ci_lower": 0.5312098757500985,
        "obs_ci_upper": 4.333055296914883,
        "rate_conservative": 0.4955641780029095,
        "treatment": 1,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": -5,
        "income": 0.003231334765282966,
        "mean": 2.0495957187450218,
        "mean_ci_lower": 1.9444911221075742,
        "mean_ci_upper": 2.154700315382469,
        "mean_se": 0.0535615168098355,
        "obs_ci_lower": 0.14920574844473689,
        "obs_ci_upper": 3.949985689045307,
        "rate_conservative": 0.4955641780029095,
        "treatment": 1,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": -4,
        "income": 0.003231334765282966,
        "mean": 1.6670588511575528,
        "mean_ci_lower": 1.5699318920418512,
        "mean_ci_upper": 1.7641858102732544,
        "mean_se": 0.04949609645816715,
        "obs_ci_lower": -0.23290659831005822,
        "obs_ci_upper": 3.567024300625164,
        "rate_conservative": 0.4955641780029095,
        "treatment": 1,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": -3,
        "income": 0.003231334765282966,
        "mean": 1.2845219835700838,
        "mean_ci_lower": 1.1937910710730781,
        "mean_ci_upper": 1.3752528960670896,
        "mean_se": 0.04623665805638643,
        "obs_ci_lower": -0.6151272370667518,
        "obs_ci_upper": 3.1841712042069195,
        "rate_conservative": 0.4955641780029095,
        "treatment": 1,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": -2,
        "income": 0.003231334765282966,
        "mean": 0.9019851159826151,
        "mean_ci_lower": 0.8157161579458508,
        "mean_ci_upper": 0.9882540740193794,
        "mean_se": 0.043962836963182275,
        "obs_ci_lower": -0.9974562219123846,
        "obs_ci_upper": 2.801426453877615,
        "rate_conservative": 0.4955641780029095,
        "treatment": 1,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": -1,
        "income": 0.003231334765282966,
        "mean": 0.5194482483951464,
        "mean_ci_lower": 0.4353985601048724,
        "mean_ci_upper": 0.6034979366854203,
        "mean_se": 0.04283189257411597,
        "obs_ci_lower": -1.3798935884223575,
        "obs_ci_upper": 2.4187900852126503,
        "rate_conservative": 0.4955641780029095,
        "treatment": 1,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": 0,
        "income": 0.003231334765282966,
        "mean": 0.1369113808076775,
        "mean_ci_lower": 0.052660864931696166,
        "mean_ci_upper": 0.22116189668365885,
        "mean_se": 0.04293423472138522,
        "obs_ci_lower": -1.7624393536300058,
        "obs_ci_upper": 2.0362621152453606,
        "rate_conservative": 0.4955641780029095,
        "treatment": 1,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": 1,
        "income": 0.003231334765282966,
        "mean": -0.24562548677979124,
        "mean_ci_lower": -0.3324801417602774,
        "mean_ci_upper": -0.15877083179930507,
        "mean_se": 0.0442613093202462,
        "obs_ci_lower": -2.1450935160120226,
        "obs_ci_upper": 1.65384254245244,
        "rate_conservative": 0.4955641780029095,
        "treatment": 1,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": 2,
        "income": 0.003231334765282966,
        "mean": -0.62816235436726,
        "mean_ci_lower": -0.7198198423370006,
        "mean_ci_upper": -0.5365048663975194,
        "mean_se": 0.04670884280706545,
        "obs_ci_lower": -2.527856055489765,
        "obs_ci_upper": 1.271531346755245,
        "rate_conservative": 0.4955641780029095,
        "treatment": 1,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": 3,
        "income": 0.003231334765282966,
        "mean": -1.010699221954729,
        "mean_ci_lower": -1.1090366077894183,
        "mean_ci_upper": -0.9123618361200398,
        "mean_se": 0.05011293238285814,
        "obs_ci_lower": -2.910726933446432,
        "obs_ci_upper": 0.889328489536974,
        "rate_conservative": 0.4955641780029095,
        "treatment": 1,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": 4,
        "income": 0.003231334765282966,
        "mean": -1.3932360895421976,
        "mean_ci_lower": -1.499777959937885,
        "mean_ci_upper": -1.28669421914651,
        "mean_se": 0.054293954448389525,
        "obs_ci_lower": -3.293706092760088,
        "obs_ci_upper": 0.5072339136756929,
        "rate_conservative": 0.4955641780029095,
        "treatment": 1,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": 5,
        "income": 0.003231334765282966,
        "mean": -1.7757729571296665,
        "mean_ci_lower": -1.8917207090904353,
        "mean_ci_upper": -1.6598252051688978,
        "mean_se": 0.05908721087748012,
        "obs_ci_lower": -3.6767934578524635,
        "obs_ci_upper": 0.12524754359313017,
        "rate_conservative": 0.4955641780029095,
        "treatment": 1,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": 6,
        "income": 0.003231334765282966,
        "mean": -2.158309824717135,
        "mean_ci_lower": -2.284596698796882,
        "mean_ci_upper": -2.032022950637388,
        "mean_se": 0.06435604859620374,
        "obs_ci_lower": -4.059988934753429,
        "obs_ci_upper": -0.2566307146808411,
        "rate_conservative": 0.4955641780029095,
        "treatment": 1,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": 7,
        "income": 0.003231334765282966,
        "mean": -2.540846692304604,
        "mean_ci_lower": -2.6781953373202922,
        "mean_ci_upper": -2.403498047288916,
        "mean_se": 0.0699931496259112,
        "obs_ci_lower": -4.44329241118103,
        "obs_ci_upper": -0.6384009734281777,
        "rate_conservative": 0.4955641780029095,
        "treatment": 1,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": 8,
        "income": 0.003231334765282966,
        "mean": -2.923383559892073,
        "mean_ci_lower": -3.072355732975473,
        "mean_ci_upper": -2.774411386808673,
        "mean_se": 0.0759165232356868,
        "obs_ci_lower": -4.826703756636905,
        "obs_ci_upper": -1.0200633631472404,
        "rate_conservative": 0.4955641780029095,
        "treatment": 1,
        "vote_conservative": 0.6037364798426745
      },
      {
        "Partisanship": "Democrat",
        "age": 43.49360865290069,
        "gender": 0.4837758112094395,
        "group": "a",
        "ideology": 9,
        "income": 0.003231334765282966,
        "mean": -3.3059204274795424,
        "mean_ci_lower": -3.4669562892044055,
        "mean_ci_upper": -3.1448845657546793,
        "mean_se": 0.08206420357156388,
        "obs_ci_lower": -5.210222822516913,
        "obs_ci_upper": -1.4016180324421716,
        "rate_conservative": 0.4955641780029095,
        "treatment": 1,
        "vote_conservative": 0.6037364798426745
      }
    ]
  },
  "facet": {
    "field": "Partisanship",
    "type": "nominal"
  },
  "params": [
    {
      "bind": "scales",
      "name": "param_21",
      "select": {
        "encodings": [
          "x",
          "y"
        ],
        "type": "interval"
      },
      "views": [
        "view_22"
      ]
    }
  ],
  "spec": {
    "layer": [
      {
        "encoding": {
          "color": {
            "field": "treatment",
            "type": "nominal"
          },
          "x": {
            "field": "ideology",
            "title": "Ideolpty",
            "type": "quantitative"
          },
          "y": {
            "field": "mean",
            "title": "Predicted values",
            "type": "quantitative"
          }
        },
        "mark": {
          "type": "line"
        },
        "name": "view_22"
      },
      {
        "encoding": {
          "color": {
            "field": "treatment",
            "title": "Treatment group",
            "type": "nominal"
          },
          "size": {
            "value": 1
          },
          "strokeDash": {
            "value": [
              5,
              3
            ]
          },
          "x": {
            "field": "ideology",
            "title": "Ideolpty",
            "type": "quantitative"
          },
          "y": {
            "field": "mean_ci_lower",
            "title": "Predicted values",
            "type": "quantitative"
          }
        },
        "mark": {
          "type": "line"
        }
      },
      {
        "encoding": {
          "color": {
            "field": "treatment",
            "type": "nominal"
          },
          "size": {
            "value": 1
          },
          "strokeDash": {
            "value": [
              5,
              3
            ]
          },
          "x": {
            "field": "ideology",
            "title": "Ideolpty",
            "type": "quantitative"
          },
          "y": {
            "field": "mean_ci_upper",
            "title": "Predicted values",
            "type": "quantitative"
          }
        },
        "mark": {
          "type": "line"
        }
      }
    ]
  }
}
```

## References

-   Fournier, P., Soroka, S., & Nir, L. (2020). Negativity Biases and
    Political Ideology: A Comparative Test across 17 Countries. American
    Political Science Review, 114(3), 775--791.
    <http://dx.doi.org/10.1017/S0003055420000131>
