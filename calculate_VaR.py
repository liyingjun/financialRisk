# -*- coding: utf-8 -*-

import akshare as ak
import numpy as np
import os
import pandas as pd
from scipy.stats import norm
import sys
import tushare as ts


def main():
    ts_code = sys.argv[1]
    start_date = sys.argv[2]
    end_date = sys.argv[3]

    # 通过tushare获取数据
    #token = sys.argv[4]

    ## 设置token
    #ts.set_token(token)

    ## 初始化pro接口
    #pro = ts.pro_api()

    #ts_code_file = ts_code + ".csv"
    #if os.path.isfile(ts_code_file):
    #    df = pd.read_csv(ts_code_file)
    #else:
    #    # 获取拓维最近一年的股票收盘价数据
    #    df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)

    #    df.to_csv(ts_code_file,encoding='gbk')  #导出为csv文件

    # 计算每日收益率
    # returns = df['pct_chg'].pct_change().dropna()

    stock_history_file = ts_code + ".csv"
    # 通过akshare获取数据
    if os.path.isfile(stock_history_file):
        df = pd.read_csv(stock_history_file, encoding='gbk')
    else:
        # 获取公司历史行情数据
        df = ak.stock_zh_a_hist(symbol=ts_code[2:], period="daily",
                                start_date=start_date,
                                end_date=end_date, adjust="qfq")
        # 导出为csv文件
        df.to_csv(stock_history_file, encoding='gbk')

    # 行逆序
    df = df.iloc[::-1]

    # 计算每日收益率
    returns = df['收盘'].pct_change().dropna()

    # 定义置信水平，投资本金
    confidence_level = 0.95
    capital = 100000

    history_var(returns, capital, confidence_level)
    std_var(returns, capital, confidence_level)
    monte_var(returns, capital, confidence_level)


def history_var(returns, capital, confidence_level):
    # 计算VaR
    VaR = returns.quantile(1 - confidence_level) * capital

    print(f'使用历史模拟法计算在{confidence_level*100}%的置信水平下，VaR为{VaR:.2f}元')
    return VaR


def std_var(returns, capital, confidence_level):
    mean = returns.mean()
    sigma = returns.std()
    # 计算VaR
    VaR = norm.ppf(1 - confidence_level, mean, sigma) * capital

    print(f'使用参数法计算在{confidence_level*100}%的置信水平下，VaR为{VaR:.2f}元')
    return VaR


def monte_var(returns, capital, confidence_level):
    # 通过历史收益数据均值和标准差生成10000个正态分布随机数，代表未来的收益率
    simulated_returns = np.random.normal(returns.mean(), returns.std(), 10000)
    # 计算VaR
    VaR = np.percentile(simulated_returns, (1 - confidence_level) * 100) * capital
    print(f'使用蒙特卡罗模拟法计算在{confidence_level*100}%的置信水平下，VaR为{VaR:.2f}元')
    return VaR


main()
