"""Offline final refit from the exact 1,260 training rows; standard library only."""
from pathlib import Path
from decimal import Decimal,localcontext
import argparse
import csv
import json
import statistics

ROOT=Path(__file__).resolve().parents[1]

def calculate(training,inputs):
    with training.open(encoding='utf-8-sig',newline='') as stream:rows=list(csv.DictReader(stream))
    assert len(rows)==1260
    assert all(row['target_date']<=inputs['origin'] for row in rows)
    assert max(row['date'] for row in rows)=='2026-11-04'
    x=[float(row['ratio']) for row in rows];y=[float(row['actual_return']) for row in rows]
    fit=statistics.linear_regression(x,y)
    with localcontext() as context:
        context.prec=50
        xx=[Decimal(str(v)) for v in x];yy=[Decimal(str(v)) for v in y]
        mx=sum(xx)/Decimal(len(xx));my=sum(yy)/Decimal(len(yy))
        slope=sum((u-mx)*(v-my) for u,v in zip(xx,yy))/sum((u-mx)**2 for u in xx)
        intercept=my-slope*mx
        assert abs(float(slope)-fit.slope)<1e-12 and abs(float(intercept)-fit.intercept)<1e-12
    ratio=inputs['VIX3M']/inputs['VIX'];predicted_return=fit.intercept+fit.slope*ratio
    price=inputs['origin_close']*(1+predicted_return)
    return {'origin':inputs['origin'],'target':inputs['target'],'training_n':len(rows),
            'training_start':min(row['date'] for row in rows),'training_end':max(row['date'] for row in rows),
            'latest_training_target':max(row['target_date'] for row in rows),
            'alpha':fit.intercept,'beta':fit.slope,'ratio':ratio,
            'predicted_return_decimal':predicted_return,'predicted_return_pct':100*predicted_return,
            'unrounded_forecast':price,'final_forecast':f'{price:.2f}',
            'independent_decimal_check':'PASS'}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--training',type=Path,default=ROOT/'01_Data/final_training_1260.csv')
    parser.add_argument('--inputs',type=Path,default=ROOT/'01_Data/final_inputs.json')
    args=parser.parse_args()
    result=calculate(args.training,json.loads(args.inputs.read_text(encoding='utf-8')))
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
