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

# summary
compare(processing_time).print()

compare_plot(processing_time, n=num_rows, rep=m)
fns = ["./tables-and-figures/" + f'filter.png']
[plt.savefig(fn) for fn in fns]

print(# "#+begin_src org \n"# # # 
    # "#+ATTR_ORG: :width 200/250/300/400/500/600\n"
    # "#+ATTR_LATEX: :width 1\textwidth :placement [ht!]\n"
    # "#+CAPTION: Comparing performance for pivot_wide()\n"
    # "#+Name: fig-pivot-wide\n"
    "[[./tables-and-figures/filter.png]]\n"
    # "#+end_src\n"# # # 
)
