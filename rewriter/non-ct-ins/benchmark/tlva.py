import click
import os
import glob
import pandas as pd
from pathlib import Path
from scipy.stats import ks_2samp
import numpy as np
from scipy.stats import ttest_ind


@click.argument("data_dir")
@click.command()
def tlva(data_dir):
    df_static = pd.read_csv(
        data_dir + "/" + "static.csv",
        header=None,
        engine="c",
        low_memory=False,
    ).transpose()
    df_randomized = pd.read_csv(
        data_dir + "/" + "randomized.csv",
        header=None,
        engine="c",
        low_memory=False,
    ).transpose()

    print("[+] Finished reading data")
    print("Static samples:", len(df_static.columns))
    print("Randomized samples:", len(df_randomized.columns))

    print("[+] TLVA leakage test")
    res_df = pd.DataFrame()

    # Auto computed
    ttest_res = ttest_ind(df_static, df_randomized, axis=1, equal_var=False)
    print(f"[+] T: {round(ttest_res.statistic[0],2)} PV: {round(ttest_res.pvalue[0],2)}")


if __name__ == "__main__":
    tlva()
