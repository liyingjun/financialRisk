# -*- coding: utf-8 -*-

import os
import sys
import tushare as ts
import numpy as np
import pandas as pd


def main():
    ts_code = sys.argv[1]
    start_date = sys.argv[2]
    end_date = sys.argv[3]
    token = sys.argv[4]

    # 设置token
    ts.set_token(token)

    # 初始化pro接口
    pro = ts.pro_api()

    ts_code_file = ts_code + ".csv"
    if os.path.isfile(ts_code_file):
        df = pd.read_csv(ts_code_file)
    else:
        # 获取拓维最近一年的股票收盘价数据
        df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)

        df.to_csv(ts_code_file,encoding='gbk')  #导出为csv文件

    # 计算每日收益率
    returns = df['pct_chg'].dropna()

    # 定义置信水平，投资本金以及持有期
    confidence_level = 0.95
    capital = 100000
    holding_period = 1

    history_var(returns, capital, confidence_level)
    std_var(returns, capital, confidence_level, holding_period)
    monte_var(returns, capital, confidence_level)


def history_var(returns, capital, confidence_level):
    # 按照收益率从小到大排序
    sorted_returns = returns.sort_values()

    # 找到第5%分位数对应的索引
    index = int(len(returns) * (1 - confidence_level))

    # 计算VaR
    VaR = sorted_returns.iloc[index] * capital

    print(f'使用历史模拟法计算在{confidence_level*100}%的置信水平下，VaR为{VaR:.2f}元')
    return VaR


def std_var(returns, capital, confidence_level, holding_period):
    # 计算历史年化波动率
    historical_volatility = returns.std() * np.sqrt(252)

    # 计算VaR
    VaR = -capital * (1 - confidence_level) * historical_volatility * np.sqrt(holding_period)

    print(f'使用参数法计算在{confidence_level*100}%的置信水平下，VaR为{VaR:.2f}元')
    return VaR


def monte_var(returns, capital, confidence_level):
    # 通过历史收益数据均值和标准差生成10000个正态分布随机数，代表未来的收益率
    simulated_returns = np.random.normal(returns.mean(), returns.std(), 10000)
    # 根据每次模拟的每日收益率，计算出每次模拟的投资组合价值
    simulated_portfolios = capital * (1 + simulated_returns)
    # 计算VaR
    VaR = np.percentile(simulated_portfolios, (1 - confidence_level) * 100)
    print(f'使用蒙特卡罗模拟法法计算在{confidence_level*100}%的置信水平下，VaR为{VaR:.2f}元')
    return VaR


main()
