"""Reproduce the report's 100-factor MAPE ranking from a frozen feature matrix."""
from pathlib import Path
import argparse
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from src.forecasting import np, pd, fit_forecasts, error_percent, ranking, RATIO

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--features',type=Path,default=Path(__file__).resolve().parents[1]/'01_Data/features100.csv.gz',help='Frozen 100-factor matrix (CSV or gzip CSV)')
    parser.add_argument('--catalog',type=Path,default=Path(__file__).resolve().parents[1]/'01_Data/factor_catalog.csv')
    parser.add_argument('--output',type=Path,default=Path('reproduced_results/single_factor'))
    args=parser.parse_args()
    f=pd.read_csv(args.features,parse_dates=['date','target_date','issue_date'])
    catalog=pd.read_csv(args.catalog);factors=catalog.factor.tolist()
    assert len(factors)==len(set(factors))==100
    assert f.date.is_unique and f.date.is_monotonic_increasing
    observed=f.target_date.notna()
    assert np.array_equal(f.target_date[observed].to_numpy(),f.date.shift(-6)[observed].to_numpy())
    assert np.allclose(f.actual_return[observed],(f.close.shift(-6)/f.close-1)[observed],rtol=1e-12,atol=1e-12)
    origins=f.index[(f.date>='2025-04-10')&(f.date<='2026-10-15')&observed].to_numpy()
    assert len(origins)==381
    predictions=fit_forecasts(f,factors,origins)
    losses=error_percent(predictions,f)
    ranks=ranking(losses,factors)
    ranks.insert(0,'rank',range(1,len(ranks)+1))
    ranks['name']=ranks.factor.map(catalog.set_index('factor').name)
    later=losses.iloc[254:]
    assert len(later)==127
    models=[RATIO,'historical_mean','no_change']
    summary={'origins':381,'origin_start':str(predictions.index.min().date()),'origin_end':str(predictions.index.max().date()),
             'best_factor':ranks.iloc[0].factor,'best_MAPE_pct':float(ranks.iloc[0].MAPE_pct),
             'full_MAPE_pct':{m:float(losses[m].mean()) for m in models},
             'later_origins':127,'later_MAPE_pct':{m:float(later[m].mean()) for m in models},
             'warning':'The later period overlaps the full selection sample; it is not an untouched holdout.'}
    args.output.mkdir(parents=True,exist_ok=True)
    ranks.to_csv(args.output/'factor_rankings.csv',index=False)
    predictions.to_csv(args.output/'forecasts.csv')
    (args.output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(ranks.head(10).to_string(index=False))
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
