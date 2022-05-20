import numpy as np
import pandas as pd
import csv
#市场的系统风险



def capm(start, end, stock):
    # print(f'CAPM for stock {stock}:')

    # 获取数据
    df = pd.read_csv('data.csv', index_col=0)
    df.index = pd.DatetimeIndex(df.index)
    df = df[df.index > start]
    df = df[df.index < end]

    df2 = pd.read_csv('fivefactor_daily.csv',index_col=0)
    df2.index = pd.DatetimeIndex(df2.index)
    df2 = df2[df2.index > start]
    df2 = df2[df2.index < end]




    # 重采样
    df = df.resample('M').last()
    df2 = df2.resample('M').last()
    risk_free_return = df2['rf']*30



    # 获取符合条件的数据
    data = pd.DataFrame({'s_close':df[f'{stock}_close'], 'm_close': df['shanghai_close']},
                        index=df.index)

    # 计算log(n)/log(n-1)来计算市场与股票回报率
    data[['s_returns', 'm_returns']] = np.log(data[['s_close', 'm_close']] / data[['s_close', 'm_close']].shift(1))

    # 去掉空值
    data = data.dropna()

    # 获得相关矩阵
    covmat = np.cov(data["s_returns"], data["m_returns"])

    # 使用矩阵计算beta
    beta_m = covmat[0, 1] / covmat[1, 1]
    # print("Beta from formula: ", beta_m)

    # 使用回归计算beta
    beta_r, alpha = np.polyfit(data["m_returns"], data["s_returns"], deg=1)
    # print("Beta from regression: ", beta_r)

    # 计算期望收益率
    expected_return_m = risk_free_return.mean() + beta_m * (data["m_returns"] - risk_free_return).mean()
    expected_return_r = risk_free_return.mean() + beta_r * (data["m_returns"] - risk_free_return).mean()
    # print("Expected Return matrix: ", expected_return_m)
    # print("Expected Return regression: ", expected_return_r)
    return expected_return_m, expected_return_r

def get_stock_list(path):
    df = pd.read_csv(path)
    stock = []
    stock_list = df.columns.values.tolist()[2:]
    for s in stock_list:
        stock.append(int(s[:-6]))
    print(stock)
    return stock

if __name__ == "__main__":
    #取得数据集中有的股票代码
    stocks = get_stock_list('data.csv')
    expected_return_m = []
    expected_return_r = []

    #输入任意股票代码获得预期回报率
    for stock in stocks:
        r1,r2 = capm('2020-11-22', '2021-12-7', stock)
        expected_return_m.append(format(r1,'.4f'))
        expected_return_r.append(format(r2,'.4f'))

    print(expected_return_r)
    print(expected_return_m)
    print(sorted(expected_return_r))
    print(sorted(expected_return_m))


    index1 = np.array(expected_return_r).argmax()
    index2 = np.array(expected_return_m).argmax()
    stock1 = stocks[index1]
    stock2 = stocks[index2]
    print(f'使用回归计算的最大收益率股票为：{stock1}，收益率为{max(expected_return_r)}')
    print(f'使用矩阵计算的最大收益率股票为：{stock2}，收益率为{max(expected_return_m)}')

    with open('capm.csv','w') as fp:
        writer = csv.writer(fp)
        for i in range(10):
            k = i+1
            writer.writerow(expected_return_r[i*5:k*5])
