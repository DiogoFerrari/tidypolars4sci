from docs.src.config import *

import tidypolars4sci as tp
import tools4sci as t4
from tidypolars4sci.data import vote as df
# 
from statsmodels.formula.api import ols as lm
from statsmodels.formula.api import glm as glm
from statsmodels.api import families as family

# variables:
df.__codebook__.print()

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
    return pred

res = (df
       .nest('partisanship')
       .crossing(outcome = ['rate_conservative', "vote_conservative"],
                 adjusted = ['Yes', 'No'])
       .mutate(
           model = tp.case_when(tp.col("outcome").str.contains('rate'), 'Linear',
                                tp.col("outcome").str.contains('vote'), 'Logit'),
           formula = tp.map(['outcome', 'adjusted'], lambda row: create_formula(*row)))
       .mutate(
           fit     = tp.map(['data', 'model', 'formula'], lambda row: estimate(*row)),
           summ    = tp.map(["fit"], lambda fit: get_summary(*fit)),
           pred    = tp.map(["fit", "data"], lambda row: predict(*row,
                                                                 at={'treatment':[0, 1],
                                                                     'ideology':range(-10, 10)}))
       )
       )
res

# explanation:
# res = (df
#        .nest('partisanship')
#        # This expands the grouped data to estimate different models 
#        # (LPM and Logit), each with and without adjustment
#        .crossing(outcome = ['rate_conservative', "vote_conservative"],
#                  adjusted = ['Yes', 'No'])
#        .mutate(
#            # this indicates with model will be estimated depending on
#            # the outcome variable
#            # rate_coservative: continuous => linear model
#            # vote_coservative: binary     => logit model
#            model = tp.case_when(tp.col("outcome").str.contains('rate'), 'Linear',
#                                 tp.col("outcome").str.contains('vote'), 'Logit'),
#            # this performs a row-wise operation, creating the regression
#            # formula depending on the outcome and if the estimation is
#            # adjusted (the * used in *row unpacks the columns for the function)
#            formula = tp.map(['outcome', 'adjusted'], lambda row: create_formula(*row)))
#        .mutate(
#            # fit the models
#            fit     = tp.map(['data', 'model', 'formula'], lambda row: estimate(*row)),
#            # create tidy summaries
#            summ    = tp.map(["fit"], lambda fit: get_summary(*fit)),
#            # create table with predicted values 'at' specified values
#            pred    = tp.map(["fit", "data"], lambda row: predict(*row,
#                                                                  at={'treatment':[0, 1],
#                                                                      'ideology':range(-10, 10)}))
#        )
#        )

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

pty = 'democrat'
model = 'Logit'
adjusted = 'Yes'
tab = (res
       .filter(tp.col("partisanship")==pty)
       .filter(tp.col("model")==model)
       .filter(tp.col("adjusted")==adjusted)
       .pull("summ")
       )

# result of the first model estimated
tab[0].print()

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

# here is the latex version
print(tabl)


tab = tab.mutate(groups = np.array(['Baseline']*2 +
                                   ['Core effects']*6 + 
                                   ['Demographics']*6 +
                                   ['Fit statistics']*6
                                   )
                 )
tab.print()


tabl = tab.to_latex(group_rows_by='groups', escape=False)
print(tabl)


