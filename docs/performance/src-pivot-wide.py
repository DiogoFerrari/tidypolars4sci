from docs.src.config import *
from docs.src.performance import *
# 
import tidypolars4sci as tp
from tidypolars4sci.data import mtcars
import time

mtcars.glimpse()

tab = (mtcars
       .select('name', 'am')
       .pivot_wider(values_from='name', names_from='am')
       )
print(tab)

df_tp = mtcars
df_pd = mtcars.to_pandas()
df_pl = mtcars.to_polars()

def pivot_wide_with_pandas(df):
    tab=(df
         .filter(['name', "am"])
         .pivot_table(index=None, values="name", columns="am",
                      aggfunc=lambda col: "; ".join(sorted(col))
                      )
         )
    
def pivot_wide_with_polars(df):
    tab = (df
           .select(["name", "am"])
           .with_columns(idx=0)
           .pivot(index='idx', on="am", values="name",
                  aggregate_function=pl.element().sort().str.concat("; ")
                  )
           )

def pivot_wide_with_tidypolars4sci(df):
    tab = (df
           .select("name", 'am')
           .pivot_wider(values_from="name", names_from='am',
                        values_fn=pl.element().sort().str.concat("; "))
           )

n = mtcars.nrow # sample size
m = 1_000       # repetitions

# collect processing time
processing_time = {'pandas': [],
                   'polars': [],
                   'tidypolars4sci': [],
                   }
# 
for i in range(m):
    # pandas
    start_time = time.time()
    pivot_wide_with_pandas(df_pd)
    processing_time['pandas'] += [time.time() - start_time]
    
    # polars
    start_time = time.time()
    pivot_wide_with_polars(df_pl)
    processing_time['polars'] += [time.time() - start_time]
    
    start_time = time.time()
    pivot_wide_with_tidypolars4sci(mtcars)
    processing_time['tidypolars4sci'] += [time.time() - start_time]

compare(processing_time).print(digits=5)

compare_plot(processing_time, n=n, rep=m)
# # Save figures
fns = ["./tables-and-figures/" + f'fig-pivot-wide.png']
[plt.savefig(fn) for fn in fns]


print("[[./tables-and-figures/pivot-wide.png]]\n"
      # "#+begin_src org \n"# # # 
      # "#+ATTR_ORG: :width 200/250/300/400/500/600\n"
      # "#+ATTR_LATEX: :width 1\\textwidth :placement [ht!]\n"
      # "#+CAPTION: Comparing performance for pivot_wide()\n"
      # "#+Name: fig-pivot-wide\n"
      # "#+end_src\n"# # # 
      )
