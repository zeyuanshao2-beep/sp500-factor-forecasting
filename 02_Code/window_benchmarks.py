"""Reproduce the archived 3/5/10-year comparisons and circular block intervals."""
from pathlib import Path
import argparse
import json
import math
import numpy as np
import pandas as pd
import src.forecasting as engine

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=ROOT/'reproduced_results/window_benchmarks')
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    f=pd.read_csv(ROOT/'01_Data/frozen_market_history.csv',parse_dates=['date','target_date']).rename(columns={'ratio':'vix3m_vix'})
    origins=f.index[f.date.between('2025-04-10','2026-10-15')&f.target_date.notna()].to_numpy()
    assert len(origins)==381
    predictions={}
    for window in [756,1260,2520]:
        engine.WINDOW=window
        p=engine.fit_forecasts(f,['vix3m_vix'],origins)
        predictions[f'vix_{window}']=p.vix3m_vix
        predictions[f'mean_{window}']=p.historical_mean
        predictions['no_change']=p.no_change
    wide=pd.DataFrame(predictions);actual=f.set_index('date').actual_close.loc[wide.index]
    absolute=wide.sub(actual,axis=0).abs();loss=absolute.div(actual,axis=0)*100
    metrics=pd.DataFrame({'MAPE_pct':loss.mean(),'MAE_points':absolute.mean(),'min_APE_pct':loss.min(),'max_APE_pct':loss.max()}).rename_axis('model').reset_index()
    metrics.to_csv(args.output/'metrics.csv',index=False)
    wide.to_csv(args.output/'forecasts.csv')
    rng=np.random.default_rng(20261105);n=len(wide)
    starts=rng.integers(0,n,(3000,math.ceil(n/20)))
    ids=((starts[:,:,None]+np.arange(20))%n).reshape(3000,-1)[:,:n]
    pairs=[('vix_756','vix_1260'),('vix_756','vix_2520'),('vix_2520','vix_1260')]
    for w in [756,1260,2520]:pairs.extend([(f'vix_{w}',f'mean_{w}'),(f'vix_{w}','no_change')])
    comparisons=[]
    for model,reference in pairs:
        delta=(loss[model]-loss[reference]).to_numpy();draws=delta[ids].mean(axis=1)
        lo,hi=np.quantile(draws,[.025,.975])
        comparisons.append({'model':model,'reference':reference,'n':n,'MAPE_difference_pp':float(delta.mean()),'CI95_low':float(lo),'CI95_high':float(hi),'block_length':20,'replicates':3000})
    result=pd.DataFrame(comparisons);result.to_csv(args.output/'bootstrap_comparisons.csv',index=False)
    archived=pd.read_csv(ROOT/'04_Results/benchmark_bootstrap_tests.csv')
    numeric=['MAPE_difference_pp','CI95_low','CI95_high']
    gap=float(abs(result[numeric].to_numpy()-archived[numeric].to_numpy()).max())
    assert gap<1e-9
    print(metrics.to_string(index=False))
    print(json.dumps({'origins':381,'bootstrap_replicates':3000,'block_length':20,'archived_bootstrap_max_gap':gap,'status':'PASS'},indent=2))

if __name__=='__main__':main()
