import pandas as pd
import numpy as np
import lifelines
from tqdm import tqdm
from sklearn.impute import KNNImputer# files have an extra tab at the end resulting in an extra column
import concurrent.futures as cf
from os import getpid


def func(os_mrna):
    significant_cols = []
    for col in tqdm(os_mrna.columns[3:]):
        cphm = lifelines.CoxPHFitter(penalizer=0.1, l1_ratio=1.0)
        cphm.fit(os_mrna[["OS_OS","OS_vital_status",col]], event_col= "OS_vital_status", duration_col="OS_OS")
        if cphm.summary["p"].values[0] <= 0.05:
            significant_cols.append([col, cphm.summary["coef"].values[0], cphm.summary["p"].values[0], cphm.concordance_index_])
    return np.array(significant_cols)


if __name__ == "__main__":
    os = pd.read_csv("./data/GBM_OS_core.txt",sep="\t").iloc[:,:-1]
    mrna = pd.read_csv("./data/GBM_mRNA_core.txt",sep="\t").iloc[:,:-1]

    mrna.iloc[:,1:] = KNNImputer(n_neighbors=3, weights="uniform").fit_transform(mrna.iloc[:,1:].T).T
    mrna.head()

    os_mrna = pd.merge(os,mrna, on="feature",copy=False)

    with cf.ProcessPoolExecutor() as exec:
        for i, res in enumerate(exec.map(func, [os_mrna.iloc[:,list(range(0,1940))], os_mrna.iloc[:, list(range(0,3)) + list(range(1940,3940))],  os_mrna.iloc[:, list(range(0,3)) + list(range(3940,5940))] , os_mrna.iloc[:, list(range(0,3)) + list(range(5940,7940))] , os_mrna.iloc[:, list(range(0,3)) + list(range(7940,11880))], os_mrna.iloc[:,list(range(0,3)) + list(range(11880, 14816))] ,os_mrna.iloc[:,list(range(0,3)) + list(range(14816, 17816))]])):
            np.save(f"mrna_univar_{i}",res)