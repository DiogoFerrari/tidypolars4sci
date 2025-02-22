import tidypolars4sci as tp
import matplotlib.pyplot as plt
import seaborn as sns
import polars as pl
import pandas as pd
import numpy as np
import time

def compare(processing_time):
    baseline = np.mean(processing_time['polars'])
    tp_slower = np.mean(processing_time['tidypolars4sci'])/baseline
    pd_slower = np.mean(processing_time['pandas'])/baseline
    tab = (tp.tibble(processing_time)
           .pivot_longer(cols=tp.matches("."), names_to='Module', values_to='sec')
           .group_by('Module')
           .summarize(Mean = tp.col("sec").mean(),
                      SD = tp.col("sec").std(),
                      Min = tp.col("sec").min(),
                      Max = tp.col("sec").max(),
                      )
           .mutate(
               **{"How much slower than polars?" :
                  tp.case_when(tp.col("Module")=='polars', "1.0x (baseline)",
                               tp.col("Module")=='tidypolars4sci', f"{tp_slower:.1f}x",
                               tp.col("Module")=='pandas', f"{pd_slower:.1f}x",
                               )},
               order = tp.case_when(tp.col("Module")=='polars', 1,
                                    tp.col("Module")=='tidypolars4sci',2,
                                    tp.col("Module")=='pandas', 3,
                                    )
           )
           .arrange("order")
           .drop("order")
           )
    return tab

def compare_plot(processing_time, rep=None, n=None):
    pan = np.array(processing_time['pandas'])
    pol = np.array(processing_time['polars'])
    tid = np.array(processing_time['tidypolars4sci'])

    fig, ax = plt.subplots(nrows=2, ncols=2, figsize=[10, 6], tight_layout=True)
    #
    ax[0][0].scatter (range(len(pol)), pan/pol, color='gray', alpha=.2)
    ax[0][0].hlines (y=(pan/pol).mean(), xmin=0, xmax=len(pol), color='black', linewidth=3)
    ax[0][0].text (y=(pan/pol).mean(), x=0, s=f"Average: {(pan/pol).mean():.2}", color='black', size=12, va='bottom', weight='bold')
    ax[0][0].set_ylabel('Ratio time elapsed:\nPandas/Polars')
    ax[0][0].set_xlabel('Iteration')
    
    ax[0][1].scatter (range(len(pol)), tid/pol, color='gray', alpha=.2)
    ax[0][1].hlines (y=(tid/pol).mean(), xmin=0, xmax=len(pol), color='black' ,linewidth=3)
    ax[0][1].text (y=(tid/pol).mean(), x=0, s=f"Average: {(tid/pol).mean():.2}", color='black', size=12, va='bottom', weight='bold')
    ax[0][1].set_ylabel('Ratio time elapsed:\nTidyPolars$^{4sci}$/Polars')
    ax[0][1].set_xlabel('Iteration')
    
    sns.histplot(pan/pol, kde=True, ax=ax[1][0], edgecolor='white', color='black')
    ax[1][0].set_xlabel('Time ratio (in seconds)\nPandas/Polars')
    sns.histplot(tid/pol, kde=True, ax=ax[1][1], edgecolor='white', color='gray')
    ax[1][1].set_xlabel('Time ratio (in seconds)\nTidyPolars$^{4sci}$/Polars')
    
    for i in range(2):
        ax[0][i].hlines(y=1, xmin=0, xmax=len(pol), color='red', linestyle='--')
        ax[0][i].set_ylim(np.min([(pan/pol).min(), (tid/pol).min()]),
                          np.max([(pan/pol).max(), (tid/pol).max()]))
        ax[1][i].set_xlim(np.min([(pan/pol).min(), (tid/pol).min()]),
                          np.max([(pan/pol).max(), (tid/pol).max()]))
    # -----
    # Title
    # -----
    if rep is not None or n is not None:
        title = f"Sample size: {n:,}  ;  Repetitions: {rep}"
        fig.suptitle(title, size=11, alpha=1)
    return ax
