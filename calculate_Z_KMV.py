# -*- coding: utf-8 -*-

import akshare as ak
import numpy as np
import os
import pandas as pd
from scipy.stats import norm
import sys


def main():
    # ts_code e.g. SZ000009
    ts_code = sys.argv[1]
    # start_date e.g. 20200729
    start_date = sys.argv[2]
    # end_date e.g. 20230728
    end_date = sys.argv[3]
    balance_file = ts_code + ".balance.csv"
    profit_file = ts_code + ".profit.csv"
    stock_history_file = ts_code + ".stock.csv"

    if os.path.isfile(stock_history_file):
        sdf = pd.read_csv(stock_history_file, encoding='gbk')
    else:
        # 获取公司历史行情数据
        sdf = ak.stock_zh_a_hist(symbol=ts_code[2:], period="daily",
                                 start_date=start_date,
                                 end_date=end_date, adjust="qfq")
        # 导出为csv文件
        sdf.to_csv(stock_history_file, encoding='gbk')

    if os.path.isfile(balance_file):
        bdf = pd.read_csv(balance_file, encoding='gbk')
    else:
        # 获取公司资产负债表数据
        bdf = ak.stock_balance_sheet_by_yearly_em(symbol=ts_code)
        # 导出为csv文件
        bdf.to_csv(balance_file, encoding='gbk')

    if os.path.isfile(profit_file):
        pdf = pd.read_csv(profit_file, encoding='gbk')
    else:
        # 获取公司利润表数据
        pdf = ak.stock_profit_sheet_by_yearly_em(symbol=ts_code)
        # 导出为csv文件
        pdf.to_csv(profit_file, encoding='gbk')

    # 判断数据是否合理
    elements = (
        bdf["TOTAL_CURRENT_ASSETS"][0],
        bdf["TOTAL_CURRENT_LIAB"][0],
        bdf["UNASSIGN_RPOFIT"][0],
        bdf["SURPLUS_RESERVE"][0],
        pdf["OPERATE_PROFIT"][0],
        bdf['TOTAL_ASSETS'][0],
        bdf["TOTAL_LIABILITIES"][0],
        bdf["TOTAL_EQUITY"][0],
        pdf["TOTAL_OPERATE_INCOME"][0]
    )
    if any(element == 0 for element in elements):
        print(f"数据缺失，无法正常计算，请打开链接检查原始数据: {source}")
        sys.exit(1)

    calculate_Z(ts_code, bdf, pdf)
    calculate_KMV(ts_code, bdf, sdf)


def calculate_Z(ts_code, bdf, pdf):
    print("===Z评分计算中...")
    # 计算Z评分所需的财务数据
    source = "https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code=%s#lrb-0" % ts_code.lower()

    print(f"数据来源：{source}")

    # 营运资本 = 流动资产 - 流动负债
    working_capitals = bdf["TOTAL_CURRENT_ASSETS"] - bdf["TOTAL_CURRENT_LIAB"]

    # 留存收益 = 未分配利润 + 盈余公积
    retained_earnings = bdf["UNASSIGN_RPOFIT"] + bdf["SURPLUS_RESERVE"]
    # 营业利润
    ebits = pdf["OPERATE_PROFIT"]
    # 总资产
    total_assets = bdf['TOTAL_ASSETS']
    # 总负债
    total_liabilities = bdf["TOTAL_LIABILITIES"]
    # 股东权益合计
    total_equities = bdf["TOTAL_EQUITY"]
    # 营业收入
    sales = pdf["TOTAL_OPERATE_INCOME"]

    dates = bdf["REPORT_DATE_NAME"]
    # 使用第一代Z评分模型计算公司最近三年Z评分
    for i in range(0, 3):
        Z_score = 1.2 * (working_capitals[i] / total_assets[i]) + \
            1.4 * (retained_earnings[i] / total_assets[i]) + \
            3.3 * (ebits[i] / total_assets[i]) + \
            0.6 * (total_equities[i] / total_liabilities[i]) + \
            0.999 * (sales[i] / total_assets[i])
        print(f"{ts_code}公司{dates[i][:4]}的Z评分为{Z_score}")


def calculate_KMV(ts_code, bdf, sdf):
    print("\n===使用KMV模型计算违约概率中...")
    source = "https://quote.eastmoney.com/concept/%s.html?from=classic" % ts_code.lower()
    print(f"历史数据来源{source}")
    # 使用KMV模型计算公司1年违约概率
    # 计算对数日收益率，ln(Vt/Vt-1)
    log_returns = np.log(sdf['收盘'] / sdf['收盘'].shift(1))

    # 计算资产均值μ和波动率σ
    mu = log_returns.mean()
    volatility = log_returns.std()
    # 流动负债
    total_current_liabs = bdf["TOTAL_CURRENT_LIAB"]
    # 非流动负债
    total_noncurrent_liabs = bdf["TOTAL_NONCURRENT_LIAB"]
    # 总资产
    total_assets = bdf['TOTAL_ASSETS']

    # 计算违约距离DD
    dd = ((mu - 0.5 * volatility ** 2) * 252 + \
          np.log(total_assets[0]/(total_current_liabs[0] + total_noncurrent_liabs[0] / 2))) / (volatility * np.sqrt(252))
    # 计算违约概率N(-dd)
    default_probability = norm.cdf(-dd)
    print(f"使用KMV模型计算{ts_code}公司1年违约概率为：{default_probability:.2f}")
    return default_probability


main()
