# S&P 500 factor forecasting

标普500未来六个美股交易日收盘点位预测。本仓库整理了报告对应的因子筛选、
单因子验证、双因子扩展和最终预测代码；原项目文件保留在本地。

## 主要结果

| 项目 | 结果 |
| --- | --- |
| 预测起点 | 2026年11月12日收盘 |
| 预测目标 | 2026年11月20日收盘 |
| 最终模型 | VIX3M/VIX，含截距OLS，1,260组已实现六日收益训练样本 |
| 起点点位 | 7,592.40 |
| 预测六日收益率 | 0.493% |
| 预测收盘点位 | **7,629.84** |

数值计算使用完整精度；报告中的一般数据展示三位小数，点位展示两位小数。

## 快速复算最终预测

Python 3.11或更新版本。最终预测脚本只使用Python标准库，可直接离线运行：

```bash
python scripts/final_forecast.py
python -m unittest discover -s tests -v
```

训练因子日期为2021-10-28至2026-11-04；全部1,260个六日目标收益均在
2026-11-12或之前实现。脚本通过`statistics.linear_regression`与50位Decimal
中心矩公式交叉检查OLS系数，并拒绝尚未实现的训练标签。

## 因子筛选与双因子扩展

```bash
python -m pip install -r requirements.txt
python scripts/screen_factors.py --features data/local/revised_features100.csv
python scripts/two_factor_extension.py --features data/local/revised_features100.csv
```

完整100因子矩阵未随代码上传，准备方法与本地归档位置见[data/README.md](data/README.md)。
每次拟合仅使用相应起点已实现的最近1,260组结果；同一381个历史起点用于统一比较。
因子排名、点位预测和汇总写入`results/`，不覆盖输入。

单因子全期最低MAPE为VIX3M/VIX的1.402%。最佳双因子加入30年减10年美债利差，
MAPE为1.384%，改善0.018个百分点。但配对区块自助法95%区间包含零，多重比较
调整后仍包含零，因此保留结构更简单的单因子模型。

后段127个起点与全期筛选区间重叠，应作为稳定性诊断，不是独立留出验证。
因子筛选和窗口比较属于探索性历史研究，不能将最小回测误差解释为未来表现保证。

## 文件对应关系

- `src/forecasting.py`：从原研究脚本保留的滚动OLS、误差计算、双因子拟合及区块自助法。
- `scripts/screen_factors.py`：100个单因子的排名及后段基准比较，对应报告5.1、5.2。
- `scripts/two_factor_extension.py`：固定VIX3M/VIX并逐一加入99个候选因子，对应报告5.3。
- `scripts/final_forecast.py`：最终1,260样本OLS与11月20日点位预测，对应报告5.4。
- `data/`：因子定义、最终预测所用训练样本及公开来源记录。
- `PROVENANCE.json`：原始脚本及输入文件的SHA256，记录代码整理来源。

仓库包含研究代码和复算所需的最终训练快照，不包含Word报告、对话记录、软件运行时、
原始HTTP响应头、Cookie或账号凭据。数据来源为Yahoo Finance和Cboe，详细URL见
`data/final_inputs.json`。第三方数据的使用条件由其提供者规定；本仓库未为其另行授权。
