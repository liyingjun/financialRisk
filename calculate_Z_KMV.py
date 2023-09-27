# -*- coding: utf-8 -*-

import argparse
import akshare as ak
import datetime
import numpy as np
import os
import pandas as pd
from scipy.optimize import fsolve
from scipy.stats import norm
import sys
import warnings


def main():
    parser = argparse.ArgumentParser(
        prog="calculate_Z_KMV",
        description=("获取某上市公司在指定时间段的财务数据以及股票收盘价数据，"
            "计算其的Z评分和使用KMV模型计算其1年违约概率")
    )
    parser.add_argument("code", help=("股票代码，深交所以SZ开头，"
                                      "上交所以SH开头，例如：SZ000009"))
    parser.add_argument("start",
                        type=lambda d: datetime.datetime.strptime(d, "%Y%m%d").date(),
                        help="数据开始日期，例如：20200729")
    parser.add_argument("end",
                        type=lambda d: datetime.datetime.strptime(d, "%Y%m%d").date(),
                        help="数据结束日期，例如：20230728")
    parser.add_argument("-c", "--category", choices=["1", "2"],
                        default="1",
                        help="上市公司种类，1表示制造业，2表示非制造业，默认为制造业")
    args = parser.parse_args()
    ts_code = args.code
    start_date = args.start.strftime("%Y%m%d")
    end_date = args.end.strftime("%Y%m%d")
    category = args.category
    balance_file = ts_code + ".balance.csv"
    profit_file = ts_code + ".profit.csv"
    stock_history_file = ts_code + ".stock.csv"

    if os.path.isfile(stock_history_file):
        sdf = pd.read_csv(stock_history_file, encoding="gbk")
    else:
        try:
            # 获取公司历史行情数据
            sdf = ak.stock_zh_a_hist(symbol=ts_code[2:], period="daily",
                                     start_date=start_date,
                                     end_date=end_date, adjust="hfq")
            # 导出为csv文件
            sdf.to_csv(stock_history_file, encoding="gbk")
        except KeyError:
            print(f"错误：没有找到{ts_code}的历史行情数据！")
            sys.exit(1)

    if os.path.isfile(balance_file):
        bdf = pd.read_csv(balance_file, encoding="gbk")
    else:
        try:
            # 获取公司资产负债表数据
            bdf = ak.stock_balance_sheet_by_yearly_em(symbol=ts_code)
            # 导出为csv文件
            bdf.to_csv(balance_file, encoding="gbk")
        except KeyError:
            print(f"错误：没有找到{ts_code}的资产负债表数据！")
            sys.exit(1)

    if os.path.isfile(profit_file):
        pdf = pd.read_csv(profit_file, encoding="gbk")
    else:
        try:
            # 获取公司利润表数据
            pdf = ak.stock_profit_sheet_by_yearly_em(symbol=ts_code)
            # 导出为csv文件
            pdf.to_csv(profit_file, encoding="gbk")
        except KeyError:
            print(f"错误：没有找到{ts_code}的利润表数据！")
            sys.exit(1)

    # 判断数据是否合理
    elements = (
        bdf["TOTAL_CURRENT_ASSETS"][0],
        bdf["TOTAL_CURRENT_LIAB"][0],
        bdf["UNASSIGN_RPOFIT"][0],
        bdf["SURPLUS_RESERVE"][0],
        pdf["OPERATE_PROFIT"][0],
        bdf["TOTAL_ASSETS"][0],
        bdf["TOTAL_LIABILITIES"][0],
        bdf["TOTAL_EQUITY"][0],
        pdf["TOTAL_OPERATE_INCOME"][0]
    )
    if any(element == 0 for element in elements):
        print(f"数据缺失，无法正常计算，请打开链接检查原始数据: {source}")
        sys.exit(1)

    calculate_Z(ts_code, bdf, pdf, category)
    calculate_KMV(ts_code, bdf, sdf)
    calculate_KMV_2(ts_code, bdf, sdf)


def calculate_Z(ts_code, bdf, pdf, category):
    print("=== Z评分计算中...")
    # 计算Z评分所需的财务数据
    source = "https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code=%s#lrb-0" % ts_code.lower()

    print(f"数据来源：{source}\n")

    # 营运资本 = 流动资产 - 流动负债
    working_capitals = bdf["TOTAL_CURRENT_ASSETS"] - bdf["TOTAL_CURRENT_LIAB"]

    # 留存收益 = 未分配利润 + 盈余公积
    retained_earnings = bdf["UNASSIGN_RPOFIT"] + bdf["SURPLUS_RESERVE"]
    # 营业利润
    ebits = pdf["OPERATE_PROFIT"]
    # 总资产
    total_assets = bdf["TOTAL_ASSETS"]
    # 总负债
    total_liabilities = bdf["TOTAL_LIABILITIES"]
    # 股东权益合计
    total_equities = bdf["TOTAL_EQUITY"]
    # 营业收入
    sales = pdf["TOTAL_OPERATE_INCOME"]

    dates = bdf["REPORT_DATE_NAME"]
    # 使用第一代Z评分模型计算公司最近三年Z评分
    for i in range(0, 3):
        if str(category) == "1":
            Z_score = 1.2 * (working_capitals[i] / total_assets[i]) + \
                1.4 * (retained_earnings[i] / total_assets[i]) + \
                3.3 * (ebits[i] / total_assets[i]) + \
                0.6 * (total_equities[i] / total_liabilities[i]) + \
                0.999 * (sales[i] / total_assets[i])
        else:
            Z_score = 6.56 * (working_capitals[i] / total_assets[i]) + \
                3.26 * (retained_earnings[i] / total_assets[i]) + \
                6.72 * (ebits[i] / total_assets[i]) + \
                1.05 * (total_equities[i] / total_liabilities[i])
        print(f"- {bdf['SECURITY_NAME_ABBR'][0]}（股票代码：{ts_code}）{dates[i][:4]}的Z评分为{Z_score}")


# 本函数来自知乎：https://zhuanlan.zhihu.com/p/571156389
def cal_Va_Sigma_a(V_e, Sigma_e, D, rf, t=1):
    """
    计算资产市值以及资产波动率
    :param V_e: 股权市值
    :param Sigma_e: 股权波动率
    :param D: 债务面值
    :param rf: 无风险利率
    :param t: 无风险利率对应期限
    :return: 资产市值V_a和资产波动率的Series
    """
    rf = (np.power(1 + rf, 1 / t) - 1) * t
    V_e, Sigma_e, D, rf = float(V_e), float(Sigma_e), float(D), float(rf)

    def solve_function(x):
        """
        方程组，用于根据股权市值，股权波动率，债务面值，无风险利率，求解每
        只股票的资产市值V_a和资产波动率Sigma_a

        :param x: 列表，两个未知数，分别是资产市值以及资产波动率
        :return: 方程
        """
        x0 = float(x[0])  # 资产市场价格, 未知数1
        x1 = float(x[1])  # 资产波动率，未知数2
        # 计算d1和d2
        d1 = (np.log(abs(x0)) - np.log(D) + (rf + 0.5 * (x1 ** 2)) * t) / (x1 * np.sqrt(t))
        d2 = d1 - x1 * np.sqrt(t)
        return [
            x0 * norm.cdf(d1) - D * np.exp(-rf * t) * norm.cdf(d2) - V_e,
            x0 * x1 * (norm.cdf(d1) / V_e) - Sigma_e
        ]

    e_x = np.array([V_e, Sigma_e])  # 设定一个方程求解初始值
    # 求解方程组
    # bsm方程组是一个非线性方程组，fslove求得的是局部最优解，所以不一定能得到全局最优解
    # 迭代初始值x0对结果的影响可能很大, 不合适的初值可能导致结果不收敛或偏差太大，因而爆出警告
    warnings.filterwarnings('ignore')  # 忽略warnings，有两个求解报了warning，想看warning就注释掉
    result = fsolve(solve_function, e_x)
    return pd.Series(result, index=['V_a', 'Sigma_a'])


def calculate_KMV_2(ts_code, bdf, sdf):
    print("\n=== 违约概率计算中（KMV模型，公式2）...")
    source = "https://quote.eastmoney.com/concept/%s.html?from=classic" % ts_code.lower()
    print(f"历史数据来源{source}\n")
    # 最近年报日期
    latest_date = datetime.datetime.strptime(bdf["REPORT_DATE"][0], "%Y-%m-%d %H:%M:%S").date()
    one_year_ago = (latest_date - datetime.timedelta(
        days=365))

    bond_china_file = f"bond_china.{latest_date.year}.csv"
    if os.path.isfile(bond_china_file):
        bond_china = pd.read_csv(bond_china_file, encoding="gbk")
    else:
        try:
            bond_china = ak.bond_china_yield(start_date=one_year_ago.strftime("%Y%m%d"),
                                             end_date=latest_date.strftime("%Y%m%d"))
            # 导出为csv文件
            bond_china.to_csv(bond_china_file, encoding="gbk")
        except KeyError:
            print("错误：获取国债数据失败！")
            sys.exit(1)

    stock_info_file = ts_code + ".info.csv"
    if os.path.isfile(stock_info_file):
        stock_info = pd.read_csv(stock_info_file, encoding="gbk")
    else:
        try:
            stock_info = ak.stock_zh_valuation_baidu(symbol=ts_code[2:],
                                                     indicator="总市值", period="近三年")
            # 导出为csv文件
            stock_info.to_csv(stock_info_file, encoding="gbk")
        except KeyError:
            print("错误：获取股票信息失败！")
            sys.exit(1)

    national_debt = bond_china.loc[bond_china["曲线名称"] == "中债国债收益率曲线"]
    rf = national_debt["1年"].mean() / 100
    print(f"\n1年期国债平均收益率为：{rf}")
    # 使用KMV模型计算公司1年违约概率
    # 计算对数日收益率，ln(Vt/Vt-1)
    if isinstance(sdf["日期"][0], datetime.date):
        sdf = sdf[(sdf["日期"] > one_year_ago) & (sdf["日期"] <= latest_date)]
    else:
        sdf = sdf[(sdf["日期"] > str(one_year_ago)) & (sdf["日期"] <= str(latest_date))]
    log_returns = np.log(sdf["收盘"] / sdf["收盘"].shift(1)).dropna()

    # 计算股权年化波动率σ
    volatility = log_returns.std() * np.sqrt(252)
    print(f"股权年化波动率：{volatility}")
    # 流动负债
    total_current_liabs = bdf["TOTAL_CURRENT_LIAB"]
    # 非流动负债
    total_noncurrent_liabs = bdf["TOTAL_NONCURRENT_LIAB"]
    # 总市值
    if isinstance(stock_info["date"][0], datetime.date):
        ve = stock_info.loc[stock_info["date"] == latest_date]["value"].iloc[0]
    else:
        ve = stock_info.loc[stock_info["date"] == str(latest_date)]["value"].iloc[0]
    # 数据单位为亿
    ve = ve * 100000000
    # 计算违约点
    dp = total_current_liabs + 0.5 * total_noncurrent_liabs
    # 计算资产市值和波动率
    va_sigma = cal_Va_Sigma_a(ve, volatility, dp[0], rf, 1)
    print(f"{latest_date} 股权市值：{ve}，资产市值：{va_sigma['V_a']}，波动率：{va_sigma['Sigma_a']}，违约点：{dp[0]}\n")
    # 计算违约距离
    dd = (va_sigma["V_a"] - dp[0]) / (va_sigma["V_a"] * va_sigma["Sigma_a"])
    print(f"- 违约距离：{dd}")
    default_probability = norm.cdf(-dd)
    print(f"- {bdf['SECURITY_NAME_ABBR'][0]}（股票代码：{ts_code}）1年违约概率（KMV模型）为：{default_probability * 100}%")


def calculate_KMV(ts_code, bdf, sdf):
    print("\n=== 违约概率计算中（KMV模型，公式1）...")
    source = "https://quote.eastmoney.com/concept/%s.html?from=classic" % ts_code.lower()
    print(f"历史数据来源{source}\n")
    # 使用KMV模型计算公司1年违约概率
    # 计算对数日收益率，ln(Vt/Vt-1)
    latest_date = datetime.datetime.strptime(bdf["REPORT_DATE"][0], "%Y-%m-%d %H:%M:%S").date()
    one_year_ago = (latest_date - datetime.timedelta(
        days=365))
    if isinstance(sdf["日期"][0], datetime.date):
        sdf = sdf[(sdf["日期"] > one_year_ago) & (sdf["日期"] <= latest_date)]
    else:
        sdf = sdf[(sdf["日期"] > str(one_year_ago)) & (sdf["日期"] <= str(latest_date))]
    log_returns = np.log(sdf["收盘"] / sdf["收盘"].shift(1)).dropna()

    # 计算资产收益率均值μ和波动率σ
    mu = log_returns.mean()
    volatility = log_returns.std()
    # 流动负债
    total_current_liabs = bdf["TOTAL_CURRENT_LIAB"]
    # 非流动负债
    total_noncurrent_liabs = bdf["TOTAL_NONCURRENT_LIAB"]
    # 总资产
    total_assets = bdf["TOTAL_ASSETS"]

    # 计算违约距离DD
    dd = ((mu - 0.5 * volatility ** 2) * 252 + \
          np.log(total_assets[0]/(total_current_liabs[0] + total_noncurrent_liabs[0] / 2))) / (volatility * np.sqrt(252))
    print(f"- 违约距离：{dd}")
    # 计算违约概率N(-dd)
    default_probability = norm.cdf(-dd)
    print(f"- {bdf['SECURITY_NAME_ABBR'][0]}（股票代码：{ts_code}）1年违约概率（KMV模型）为：{default_probability * 100}%")
    return default_probability


main()
