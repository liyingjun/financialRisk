# 金融风险计算脚本

## 安装基础环境

1. 下载并安装最新版本的Python: https://www.python.org/downloads/
2. 安装pip：https://pip.pypa.io/en/stable/installation/
3. 安装依赖：`pip install -r requirements.txt`

## 脚本使用介绍

### calculate_VaR.py

选择最近一年内每天的某公司股票收盘价数据，用历史模拟法、参数法、蒙特卡罗模拟法
计算股票在未来一个交易日内亏损超过10万人民币的概率为5%的VaR

```
python calculate_VaR.py ts_code start_date end_date tushare_token
```

参数解释:

- ts_code: 股票代码，比如平安银行为 `000001.SZ`
- start_date: 开始日期，格式为YYYYMMDD，比如 `20220729`
- end_date: 结束日期，格式为YYYYMMDD，比如 `20230728`
- tushare_token: tushare接口TOKEN，https://tushare.pro/user/token 获取
