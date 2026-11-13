from pathlib import Path
import importlib.util
import json
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('final_forecast',ROOT/'scripts/final_forecast.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class FinalForecastChecks(unittest.TestCase):
    def setUp(self):
        self.training=ROOT/'data/final_training_1260.csv'
        self.inputs=json.loads((ROOT/'data/final_inputs.json').read_text())

    def test_frozen_forecast_and_training_boundary(self):
        result=module.calculate(self.training,self.inputs)
        self.assertEqual(result['final_forecast'],'7629.84')
        self.assertEqual(result['training_n'],1260)
        self.assertEqual(result['training_start'],'2021-10-28')
        self.assertEqual(result['training_end'],'2026-11-04')
        self.assertEqual(result['latest_training_target'],'2026-11-12')
        self.assertAlmostEqual(result['alpha'],0.056407055248279464,places=12)
        self.assertAlmostEqual(result['beta'],-0.04798580800818491,places=12)

    def test_unmatured_label_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            bad=Path(folder)/'bad.csv'
            bad.write_text(self.training.read_text().replace('2026-11-12','2026-11-13'),encoding='utf-8')
            with self.assertRaises(AssertionError):module.calculate(bad,self.inputs)

if __name__=='__main__':unittest.main()
