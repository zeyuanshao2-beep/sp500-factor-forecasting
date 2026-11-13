"""Rebuild VIX3M/VIX and six-session labels on the frozen equity calendar."""
from pathlib import Path
import csv
import json
import argparse

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--input',type=Path,default=ROOT/'01_Data/frozen_market_history.csv')
    parser.add_argument('--output',type=Path,default=ROOT/'reproduced_results/constructed_factor.csv')
    args=parser.parse_args()
    rows=list(csv.DictReader(args.input.open(encoding='utf-8-sig',newline='')))
    dates=[r['date'] for r in rows]
    assert len(dates)==len(set(dates)) and dates==sorted(dates)
    result=[]
    for i,r in enumerate(rows):
        ratio=float(r['VIX3M'])/float(r['VIX'])
        assert abs(ratio-float(r['ratio']))<1e-12
        record={k:r[k] for k in ['date','close','VIX','VIX3M']}
        record['ratio']=ratio
        record['target_date']=rows[i+6]['date'] if i+6<len(rows) else ''
        record['actual_close']=rows[i+6]['close'] if i+6<len(rows) else ''
        record['actual_return']=float(rows[i+6]['close'])/float(r['close'])-1 if i+6<len(rows) else ''
        if record['target_date']:
            assert record['target_date']==r['target_date']
            assert abs(record['actual_return']-float(r['actual_return']))<1e-12
        result.append(record)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('w',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(result[0]));writer.writeheader();writer.writerows(result)
    print(json.dumps({'rows':len(rows),'horizon_sessions':6,'last_observation':dates[-1],'ratio_and_targets_crosscheck':'PASS','output':str(args.output.relative_to(ROOT))},indent=2))

if __name__=='__main__':main()
