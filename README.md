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
python3 calculate_VaR.py ts_code start_date end_date
```

参数解释:

- ts_code: 股票代码，比如万科A为 `SZ000002`
- start_date: 开始日期，格式为YYYYMMDD，比如 `20220729`
- end_date: 结束日期，格式为YYYYMMDD，比如 `20230728`

### calculate_Z_KMV.py

获取某上市公司在指定时间段的财务数据以及股票收盘价数据，计算其的Z评分和
使用KMV模型计算其1年违约概率

```
python3 calculate_Z_KMV.py ts_code start_date end_date
```

参数解释:

- ts_code: 股票代码，比如万科A为 `SZ000002`
- start_date: 开始日期，格式为YYYYMMDD，比如 `20200729`
- end_date: 结束日期，格式为YYYYMMDD，比如 `20230728`

示例:

```
python3 calculate_Z_KMV.py SZ000002 20200729 20230728
```
