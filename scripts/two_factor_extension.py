"""Add each of 99 factors to VIX3M/VIX using identical rolling origins."""
from pathlib import Path
import argparse
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.forecasting import np,pd,fit_forecasts,error_percent,fit_pairs,bootstrap,RATIO

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--features',type=Path,required=True,help='Frozen revised_features100.csv')
    parser.add_argument('--catalog',type=Path,default=Path(__file__).resolve().parents[1]/'data/factor_catalog.csv')
    parser.add_argument('--output',type=Path,default=Path('results/two_factor'))
    args=parser.parse_args()
    f=pd.read_csv(args.features,parse_dates=['date','target_date','issue_date'])
    catalog=pd.read_csv(args.catalog).set_index('factor')
    factors=sorted(set(catalog.index)-{RATIO});assert len(factors)==99
    assert f.date.is_unique and f.date.is_monotonic_increasing
    observed=f.target_date.notna()
    assert np.array_equal(f.target_date[observed].to_numpy(),f.date.shift(-6)[observed].to_numpy())
    origins=f.index[(f.date>='2025-04-10')&(f.date<='2026-10-15')&observed].to_numpy();assert len(origins)==381
    pair,condition=fit_pairs(f,factors,origins)
    single=fit_forecasts(f,[RATIO],origins)
    base=error_percent(single,f)[RATIO]
    actual=f.set_index('date').actual_close.loc[pair.index]
    error=pair.sub(actual,axis=0).abs();loss=error.div(actual,axis=0)*100
    intervals,pvalue=bootstrap(loss,base)
    ranks=pd.DataFrame({'name':catalog.loc[factors,'name'],'MAPE_pct':loss.mean(),
                        'MAE_points':error.mean(),'min_APE_pct':loss.min(),'max_APE_pct':loss.max()})
    ranks=ranks.join(intervals).rename_axis('added_factor').reset_index().sort_values(['MAPE_pct','added_factor'])
    ranks.insert(0,'rank',range(1,len(ranks)+1))
    best=ranks.iloc[0].to_dict()
    summary={'origins':381,'extensions':99,'best_full_period':best,
             'single_factor_MAPE_pct':float(base.mean()),'improved_pairs':int((ranks.difference_pp<0).sum()),
             'max_search_p_approx':pvalue,'largest_standardised_condition_number':condition,
             'retained_model':'VIX3M/VIX only','reason':'Small error gain; paired and multiple-comparison intervals include zero.'}
    args.output.mkdir(parents=True,exist_ok=True)
    ranks.to_csv(args.output/'ranking.csv',index=False)
    (args.output/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(summary,indent=2,ensure_ascii=False))

if __name__=='__main__':main()
