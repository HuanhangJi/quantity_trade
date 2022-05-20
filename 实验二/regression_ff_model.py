import pandas as pd
from statsmodels import regression
import statsmodels.api as sm
import numpy as np

#获取股票序列
def get_stock_list():
    df = pd.read_csv('data.csv')
    stock = []
    stock_list = df.columns.values.tolist()[2:]
    for s in stock_list:
        stock.append(int(s[:-6]))
    print(stock)
    return stock

class FF_regression:
    def __init__(self,path,start,end,stock):
        data,date,mrk_rf,rf,fac1,fac2 = self.cop_data(path,start,end)
        self.data = data
        self.date = date
        self.mrf_rf = data[mrk_rf] * 30
        self.rf = data[rf] * 30
        self.fac1 = fac1
        self.fac2 = fac2
        self.fac1_d = pd.DataFrame(data,columns=fac1) * 30
        self.fac2_d = pd.DataFrame(data,columns=fac2) * 30

        #股票的回报率
        self.rr = self.data_process(start,end,stock)



    # 数据处理
    def cop_data(self,path,start,end):
        df = pd.read_csv(path,index_col=0)
        df.index = pd.DatetimeIndex(df.index)

        df = df[df.index > start]
        df = df[df.index < end]

        # 重采样
        data = df.resample('M').last()
        column = data.columns
        date = data.index

        #市场回报率
        mrk_rf = column[0]

        #无风险利率
        rf = column[6]

        # 加权的四个因子
        fac1 = column[1:6]

        #不加权的四个因子
        fac2 = column[7:]
        return data,date,mrk_rf,rf,fac1,fac2

    def data_process(self,start,end,stock):
        # 获取市场价格数据
        df = pd.read_csv('data.csv', index_col=0)
        df.index = pd.DatetimeIndex(df.index)
        df = df[df.index > start]
        df = df[df.index < end]

        # 重采样
        price_data = df.resample('M').last().drop(['shanghai_close'],axis=1)
        rr = self.return_ratio(price_data)[f'{stock}_close']
        return rr

    # 计算股票回报率
    def return_ratio(self,price_data):
        rr = ((price_data/price_data.shift(1))-1).dropna()
        return rr

    # FF3因子加权回归
    def FF3(self):
        y = np.array(self.rr - self.rf)[1:]
        Y = y.T

        column =self.fac1[0:2]
        df = pd.DataFrame(self.fac1_d,columns=column)
        X = np.column_stack((self.mrf_rf-self.rf, df))[1:]
        X = sm.add_constant(X)

        mod = regression.linear_model.OLS(Y,X).fit()
        paras = mod.params
        names = ['alpha','beta','smb_p','hml_p']
        return dict(zip(names,paras))

    # FF3因子不加权回归
    def FF3_equal(self):
        y = np.array(self.rr - self.rf)[1:]
        Y = y.T

        column = self.fac2[0:2]
        df = pd.DataFrame(self.fac2_d, columns=column)
        X = np.column_stack((self.mrf_rf - self.rf, df))[1:]
        X = sm.add_constant(X)

        mod = regression.linear_model.OLS(Y, X).fit()
        paras = mod.params
        names = ['alpha', 'beta', 'smb_p', 'hml_p']
        return dict(zip(names, paras))

    # FF5因子加权回归
    def FF5(self):
        y = np.array(self.rr - self.rf)[1:]
        Y = y.T

        column = ['smb','hml','rmw','cma']
        df = pd.DataFrame(self.fac1_d, columns=column)
        X = np.column_stack((self.mrf_rf - self.rf, df))[1:]
        X = sm.add_constant(X)

        mod = regression.linear_model.OLS(Y, X).fit()
        paras = mod.params
        names = ['alpha','beta','smb_p','hml_p','rwm_p','cma_p']
        return dict(zip(names, paras))

    # FF5因子不加权回归
    def FF5_equal(self):
        y = np.array(self.rr - self.rf)[1:]
        Y = y.T

        column = ['smb','hml','rmw','cma']
        for i in range(4):
            column[i] += '_equal'

        df = pd.DataFrame(self.fac2_d, columns=column)
        X = np.column_stack((self.mrf_rf - self.rf, df))[1:]
        X = sm.add_constant(X)

        mod = regression.linear_model.OLS(Y, X).fit()
        paras = mod.params
        names = ['alpha','beta','smb_p','hml_p','rwm_p','cma_p']
        return dict(zip(names, paras))


def get_max(li):
    index = np.argmax(np.array(li))

    m = max(li)
    return index,m


def get_ans(stocks,start,end):
    alpha3 = []
    alpha3_E = []
    alpha5 = []
    alpha5_E = []

    for stock in stocks:
        f = FF_regression('fivefactor_daily.csv', start, end, stock)
        alpha3.append(f.FF3()['alpha'])
        alpha3_E.append(f.FF3_equal()['alpha'])
        alpha5.append(f.FF5()['alpha'])
        alpha5_E.append(f.FF5_equal()['alpha'])



    print(alpha3)
    print(alpha3_E)
    print(alpha5)
    print(alpha5_E)
    print()
    print(sorted(alpha3))
    print(sorted(alpha3_E))
    print(sorted(alpha5))
    print(sorted(alpha5_E))
    i,m = get_max(alpha3)
    print(f'由FF三因子模型计算出的回报率最大的股票代号为{stocks[i]}，最大值为{m}')

    i, m = get_max(alpha3_E)
    print(f'由不加权FF三因子模型计算出的回报率最大的股票代号为{stocks[i]}，最大值为{m}')

    i, m = get_max(alpha5)
    print(f'由FF五因子模型计算出的回报率最大的股票代号为{stocks[i]}，最大值为{m}')

    i, m = get_max(alpha5_E)
    print(f'由不加权FF五因子模型计算出的回报率最大的股票代号为{stocks[i]}，最大值为{m}')




stocks = get_stock_list()
get_ans(stocks,'2020-01-22', '2022-5-11')
# F = FF_regression('fivefactor_daily.csv', '2020-01-22', '2022-5-11', 601888)
# F.FF5_equal()

