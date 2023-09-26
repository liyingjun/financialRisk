# -*- coding: utf-8 -*-

import argparse
import akshare as ak
import datetime
import numpy as np
import os
import pandas as pd
from scipy.stats import norm
import sys
import tushare as ts


def main():
    parser = argparse.ArgumentParser(
        prog="calculate_VaR",
        description=("指定本金，选择一段时间某公司股票收盘价数据，"
                     "用历史模拟法、参数法和蒙特卡罗模拟法计算股票"
                     "在未来一个日度指定置信水平的VaR"),
    )
    parser.add_argument("code", help=("股票代码，深交所以SZ开头，"
                                      "上交所以SH开头，例如：SZ000009"))
    parser.add_argument("start",
                        type=lambda d: datetime.datetime.strptime(d, "%Y%m%d").date(),
                        help="数据开始日期，例如：20200729")
    parser.add_argument("end",
                        type=lambda d: datetime.datetime.strptime(d, "%Y%m%d").date(),
                        help="数据结束日期，例如：20230728")
    parser.add_argument("-c", "--capital", type=int,
                        default="100000",
                        help="本金，默认为100000元")
    parser.add_argument("-l", "--confidence-level", type=float,
                        default="0.95",
                        help="置信水平，默认为0.95")
    args = parser.parse_args()

    ts_code = args.code
    start_date = args.start.strftime("%Y%m%d")
    end_date = args.end.strftime("%Y%m%d")

    # 定义置信水平，投资本金
    confidence_level = args.confidence_level
    capital = args.capital

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

    #    df.to_csv(ts_code_file,encoding="gbk")  #导出为csv文件

    # 计算每日收益率
    # returns = df["pct_chg"].pct_change().dropna()

    stock_history_file = ts_code + ".csv"
    # 通过akshare获取数据
    if os.path.isfile(stock_history_file):
        df = pd.read_csv(stock_history_file, encoding="gbk")
    else:
        try:
            # 获取公司历史行情数据
            df = ak.stock_zh_a_hist(symbol=ts_code[2:], period="daily",
                                    start_date=start_date,
                                    end_date=end_date, adjust="qfq")
            # 导出为csv文件
            df.to_csv(stock_history_file, encoding="gbk")
        except KeyError:
            print(f"错误：没有找到{ts_code}的数据！")
            sys.exit(1)

    source = "https://quote.eastmoney.com/concept/%s.html?from=classic" % ts_code.lower()
    print(f"历史数据来源{source}\n")

    # 行逆序
    df = df.iloc[::-1]

    # 计算每日收益率
    returns = df["收盘"].pct_change().dropna()

    print(f"VaR计算中（股票代码：{ts_code}），其中本金: {capital}元，"
          f"置信水平: {confidence_level}，持有期为1天\n")

    history_var(ts_code, returns, capital, confidence_level)
    std_var(ts_code, returns, capital, confidence_level)
    monte_var(ts_code, returns, capital, confidence_level)


def history_var(ts_code, returns, capital, confidence_level):
    # 计算VaR
    VaR = -1 * returns.quantile(1 - confidence_level) * capital

    print(f"- 使用历史模拟法计算VaR为：{VaR:.2f}元")
    return VaR


def std_var(ts_code, returns, capital, confidence_level):
    mean = returns.mean()
    sigma = returns.std()
    # 计算VaR
    VaR = -1 * norm.ppf(1 - confidence_level, mean, sigma) * capital

    print(f"- 使用参数法计算VaR为：{VaR:.2f}元")
    return VaR


def monte_var(ts_code, returns, capital, confidence_level):
    # 通过历史收益数据均值和标准差生成10000个正态分布随机数，代表未来的收益率
    simulated_returns = np.random.normal(returns.mean(), returns.std(), 10000)
    # 计算VaR
    VaR = -1 * np.percentile(simulated_returns, (1 - confidence_level) * 100) * capital
    print(f"- 使用蒙特卡罗模拟法计算VaR为：{VaR:.2f}元")
    return VaR


main()
