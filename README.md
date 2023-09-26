# 金融风险计算脚本

## 安装基础环境

1. 下载并安装最新版本的Python: https://www.python.org/downloads/
2. 安装pip：https://pip.pypa.io/en/stable/installation/
3. 点击链接下载项目到本地：https://github.com/liyingjun/financialRisk/archive/refs/heads/main.zip
4. 解压代码，进入代码目录安装依赖：`pip install --index-url https://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com -r requirements.txt`

## 脚本使用介绍

### calculate_VaR.py

以10万人民币本金出发，选择一段时间某公司股票收盘价数据,用历史模拟法、参数法和蒙特卡罗模拟法计算股票在未来一个日度5%的VaR:

```
usage: calculate_VaR [-h] [-c CAPITAL] [-l CONFIDENCE_LEVEL] code start end

指定本金，选择一段时间某公司股票收盘价数据，用历史模拟法、参数法和蒙特卡罗模拟法计算股票在未来一个日度指定置信水平的VaR

positional arguments:
  code                  股票代码，深交所以SZ开头，上交所以SH开头，例如：SZ000009
  start                 数据开始日期，例如：20200729
  end                   数据结束日期，例如：20230728

options:
  -h, --help            show this help message and exit
  -c CAPITAL, --capital CAPITAL
                        本金，默认为100000元
  -l CONFIDENCE_LEVEL, --confidence-level CONFIDENCE_LEVEL
                        置信水平，默认为0.95
```

使用示例：

```
python3 calculate_VaR.py SZ000009 20220729 20230728
```

输出：

```
历史数据来源https://quote.eastmoney.com/concept/sz000009.html?from=classic

VaR计算中（股票代码：SZ000009），其中本金: 100000元，置信水平: 0.95，持有期为1天

- 使用历史模拟法计算VaR为：3519.41元
- 使用参数法计算VaR为：3608.37元
- 使用蒙特卡罗模拟法计算VaR为：3648.19元
```

### calculate_Z_KMV.py

获取某上市公司在指定时间段的财务数据以及股票收盘价数据，计算其的Z评分和
使用KMV模型计算其1年违约概率

```
usage: calculate_Z_KMV [-h] [-c {1,2}] code start end

获取某上市公司在指定时间段的财务数据以及股票收盘价数据，计算其的Z评分和使用KMV模型计算其1年违约概率

positional arguments:
  code                  股票代码，深交所以SZ开头，上交所以SH开头，例如：SZ000009
  start                 数据开始日期，例如：20200729
  end                   数据结束日期，例如：20230728

options:
  -h, --help            show this help message and exit
  -c {1,2}, --category {1,2}
                        上市公司种类，1表示制造业，2表示非制造业，默认为制造业
```

使用示例:

- 制造业:

    ```
    python3 calculate_Z_KMV.py SH600519 20200729 20230728
    ```

    输出：

    ```
    === Z评分计算中...
    数据来源：https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code=sh600519#lrb-0

    - 贵州茅台（股票代码：SH600519）2022的Z评分为5.987720225097479
    - 贵州茅台（股票代码：SH600519）2021的Z评分为5.210991635722403
    - 贵州茅台（股票代码：SH600519）2020的Z评分为5.514636976685933

    === 违约概率计算中（KMV模型）...
    历史数据来源https://quote.eastmoney.com/concept/sh600519.html?from=classic

    - 违约距离：5.2356877080759014
    - 贵州茅台（股票代码：SH600519）1年违约概率（KMV模型）为：8.218583787275984e-06%
    ```

- 非制造业:

    ```
    python3 calculate_Z_KMV.py --category 2 SH600536 20200729 20230728
    ```

    输出：

    ```
    === Z评分计算中...
    数据来源：https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code=sh600536#lrb-0

    - 中国软件（股票代码：SH600536）2022的Z评分为1.9862590134182563
    - 中国软件（股票代码：SH600536）2021的Z评分为2.275817165241086
    - 中国软件（股票代码：SH600536）2020的Z评分为2.422785003802755

    === 违约概率计算中（KMV模型）...
    历史数据来源https://quote.eastmoney.com/concept/sh600536.html?from=classic

    - 违约距离：0.6374913343502171
    - 中国软件（股票代码：SH600536）1年违约概率（KMV模型）为：26.1902426362263%
    ```
