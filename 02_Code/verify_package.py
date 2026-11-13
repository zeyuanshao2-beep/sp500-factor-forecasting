"""Independent raw-source reconstruction and OLS verification; stdlib only."""
from pathlib import Path
from hashlib import sha256
import bisect
import csv
import datetime as dt
import gzip
import importlib.util
import json
import statistics
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def rows(p):
    opener=gzip.open if p.suffix=='.gz' else open
    with opener(p,'rt',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def yahoo(p):
    q=read(p)['chart']['result'][0]
    assert q['meta']['symbol']=='^GSPC'
    return {dt.datetime.fromtimestamp(t,dt.timezone.utc).astimezone(ZoneInfo('America/New_York')).date().isoformat():float(v)
        for t,v in zip(q['timestamp'],q['indicators']['quote'][0]['close']) if v is not None}
def vol(p):
    return {dt.datetime.strptime(r['DATE'],'%m/%d/%Y').date().isoformat():float(r['CLOSE']) for r in rows(p)}

def main():
    cutoff=dt.datetime.fromisoformat('2026-11-13T12:00:00+00:00')
    manifest=read(ROOT/'01_Data/source_manifest.json')
    for source in manifest:
        assert sha256((ROOT/source['file']).read_bytes()).hexdigest()==source['sha256']
        assert dt.datetime.fromisoformat(source['retrieved_utc'])<=cutoff
    raw=ROOT/'01_Data/raw'
    prices=yahoo(raw/'archived_yahoo_SP500_2010_2020.json')
    prices.update(yahoo(raw/'archived_yahoo_SP500_2020_2026.json'))
    extra=yahoo(raw/'final_yahoo_SP500.json')
    prices.update({k:v for k,v in extra.items() if k>'2026-10-23'})
    series={}
    for symbol in ['VIX','VIX3M']:
        old=vol(raw/f'archived_{symbol}_History.csv')
        new=vol(raw/f'final_{symbol}_History.csv')
        data={k:v for k,v in old.items() if k<='2026-10-23'}
        data.update({k:v for k,v in new.items() if k>'2026-10-23'})
        quote=read(raw/f'final_cboe_quote_{symbol}.json')
        assert quote['data']['last_trade_time']=='2026-11-12T16:15:01'
        data['2026-11-12']=float(quote['data']['close']);series[symbol]=data
    days=sorted(k for k in prices if '2010-01-04'<=k<='2026-11-12')
    data=[]
    for i,day in enumerate(days):
        ratio=series['VIX3M'][day]/series['VIX'][day]
        record={'date':day,'close':prices[day],'ratio':ratio}
        if i+6<len(days):record.update(target_date=days[i+6],actual_close=prices[days[i+6]],actual_return=prices[days[i+6]]/prices[day]-1)
        data.append(record)
    supplied=rows(ROOT/'01_Data/frozen_market_history.csv')
    assert len(supplied)==len(data)
    max_input_gap=0.
    for own,frozen in zip(data,supplied):
        assert own['date']==frozen['date']
        for key in ['close','ratio','actual_close','actual_return']:
            if key in own:
                gap=abs(own[key]-float(frozen[key]));max_input_gap=max(max_input_gap,gap)
                assert gap<1e-7
        if 'target_date' in own:assert own['target_date']==frozen['target_date']
    all_forecasts=rows(ROOT/'04_Results/window_forecasts_381x7.csv.gz')
    selected=[r for r in all_forecasts if r['model']=='vix_1260']
    assert len(selected)==381
    targets=[r['target_date'] for r in data if 'target_date' in r]
    bydate={r['date']:r for r in data};max_forecast_gap=0.;fits=0
    for r in all_forecasts:
        current=bydate[r['origin_date']]
        if r['model']=='no_change':predicted=current['close']
        else:
            window=int(r['window']);end=bisect.bisect_right(targets,current['date'])
            train=data[end-window:end]
            assert len(train)==window and train[-1]['target_date']<=current['date']
            y=[v['actual_return'] for v in train]
            if r['model'].startswith('vix_'):
                fit=statistics.linear_regression([v['ratio'] for v in train],y)
                predicted=current['close']*(1+fit.intercept+fit.slope*current['ratio']);fits+=1
            else:predicted=current['close']*(1+statistics.mean(y))
        gap=abs(predicted-float(r['predicted_close']));max_forecast_gap=max(max_forecast_gap,gap)
        assert gap<1e-7
        ape=100*abs(predicted-current['actual_close'])/current['actual_close']
        assert abs(ape-float(r['APE_pct']))<1e-9
    spec=importlib.util.spec_from_file_location('final',ROOT/'02_Code/final_forecast.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    final=module.calculate(ROOT/'01_Data/final_training_1260.csv',read(ROOT/'01_Data/final_inputs.json'))
    frozen=read(ROOT/'final_forecast.json')
    assert final['final_forecast']=='7629.84' and frozen['final_forecast_value']==float(final['final_forecast'])
    assert frozen['pdf_cover_check']['matches'] is True
    final_data=[v for v in data if v.get('target_date','9999')<='2026-11-12'][-1260:]
    assert len(final_data)==1260
    final_fit=statistics.linear_regression([v['ratio'] for v in final_data],[v['actual_return'] for v in final_data])
    assert abs(final_fit.intercept-final['alpha'])<1e-12 and abs(final_fit.slope-final['beta'])<1e-12
    # Historical dated regression example, independently re-estimated.
    dated=read(ROOT/'04_Results/original_regression_evidence.json')
    dated_rows=rows(ROOT/'04_Results/original_regression_training.csv')
    keys=list(dated_rows[0]);x_key='ratio' if 'ratio' in keys else 'vix3m_vix'
    y_key='actual_return'
    fit=statistics.linear_regression([float(r[x_key]) for r in dated_rows],[float(r[y_key]) for r in dated_rows])
    assert abs(fit.intercept-dated['alpha'])<1e-10 and abs(fit.slope-dated['beta'])<1e-10
    result={'status':'PASS','raw_source_hashes_verified':len(manifest),'market_rows_reconstructed':len(data),
        'maximum_input_gap':max_input_gap,'historical_forecast_records':len(all_forecasts),'selected_model_origins':381,
        'independent_OLS_fits':fits,'maximum_forecast_gap_points':max_forecast_gap,'horizon_sessions':6,
        'final_forecast':final['final_forecast'],'final_refit_decimal_check':final['independent_decimal_check'],
        'original_regression_crosscheck':'PASS','pdf_cover_manifest_match':'PASS',
        'limitations':'Numerical/source-snapshot verification does not verify every original publication vintage, validate causal prediction or constitute human approval.'}
    destination=ROOT/'reproduced_results/verification';destination.mkdir(parents=True,exist_ok=True)
    (destination/'independent_verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
