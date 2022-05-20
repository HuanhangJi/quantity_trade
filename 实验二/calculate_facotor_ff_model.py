import numpy as np
import pandas as pd
import random
from statsmodels import regression
import statsmodels.api as sm

class FF_model:
    def __init__(self,start,end):
        #数据处理
        self.data_process(start,end)
        # 市场无风险利率，如果能够读取就直接读取
        self.rf = 0.05

    # 这里由于收集的数据是直接的因子，无法展示具体计算过程，因此写另外一组代码展示从数据到因子的过程
    # 使用的依然是CAPM同样的数据
    def data_process(self,start,end):
        # 获取市场价格数据
        df = pd.read_csv('data.csv', index_col=0)
        df.index = pd.DatetimeIndex(df.index)
        df = df[df.index > start]
        df = df[df.index < end]

        # 重采样
        price_data = df.resample('M').last().drop(['shanghai_close'],axis=1)
        market_data = df.resample('M').last()[['shanghai_close']]

        #这里的市值也是直接用的虚拟数据，使用时需要导入
        self.mrk_cap = price_data

        #市场大盘，计算市场回报率用
        self.mrk = market_data

        #故每个股票的股价
        self.stk = price_data

        #提取日期序列与股票种类
        index_date = price_data.index
        stocks = price_data.columns
        self.index_date = index_date
        self.stocks = stocks

        # 构建book_value_per_share，这里是模拟数据，并非真是数据
        #如果是真实数据只需要导入进行与上文相同的处理即可
        book_value_per_share = pd.DataFrame(index=index_date,columns=stocks)
        for i in index_date:
            for j in stocks:
                book_value_per_share[j][i] = price_data[j][i] + random.randint(-10,10)/10.0
        self.book_value_per_share = book_value_per_share

        # 构造经营利润（营业收人减去营业成本、利息支出、销售费用、管理费用）
        revene_per_share = pd.DataFrame(index=index_date,columns=stocks)
        for i in index_date:
            for j in stocks:
                revene_per_share[j][i] = price_data[j][i] + random.randint(-10,10)/10.0
        self.revene_per_share = revene_per_share

        # 构造总资产
        property = pd.DataFrame(index=index_date,columns=stocks)
        for i in index_date:
            for j in stocks:
                property[j][i] = price_data[j][i] + random.randint(-10,10)/10.0
        self.property = property

    # 计算book to market ratio去分组
    def get_btm(self):
        btm = pd.DataFrame(index=self.index_date,columns=self.stocks)
        for i in self.index_date:
            for j in self.stocks:
                if self.stk[j][i] != 0:
                    btm[j][i] = self.book_value_per_share[j][i]/self.stk[j][i]
                else:
                    btm[j][i] = 0
        return btm

    # 计算盈利能力，为经营利润与账面价值之比
    def get_rmw(self):
        rmw = pd.DataFrame(index=self.index_date, columns=self.stocks)
        for i in self.index_date:
            for j in self.stocks:
                if self.stk[j][i] != 0:
                    rmw[j][i] = self.revene_per_share[j][i]/self.book_value_per_share[j][i]
                else:
                    rmw[j][i] = 0
        return rmw

    # 计算投资水平
    def get_cma(self):
        cma = ((self.property/self.property.shift(1))-1).dropna()
        return cma

    # HML 30% 70%分组
    def h_m_l(self,btm):
        lmark = {}
        hmark = {}
        for date in self.index_date:
            lmark[date] = np.percentile(list(btm.loc[date]), 30)
            hmark[date] = np.percentile(list(btm.loc[date]), 70)
            if lmark[date] == 0:
                lmark[date] = hmark[date]/2
        mark = {}
        mark['lmark'] = lmark
        mark['hmark'] = hmark
        return mark

    # SMB 中位数分组
    def s_m_b(self):
        meadian_size = {}
        for date in self.index_date:
            meadian_size[date] = np.median(self.mrk_cap.loc[date])
        return meadian_size

    # RMW 30% 70%分组
    def r_m_w(self,rmw):
        rmark = {}
        wmark = {}
        for date in self.index_date:
            rmark[date] = np.percentile(list(rmw.loc[date]), 30)
            wmark[date] = np.percentile(list(rmw.loc[date]), 70)
            if rmark[date] == 0:
                rmark[date] = rmark[date]/2
        mark2 = {}
        mark2['rmark'] = rmark
        mark2['wmark'] = wmark
        return mark2

    # CMA 30% 70%分组
    def c_m_a(self,cma):
        cmark = {}
        amark = {}
        i = 0
        for date in self.index_date:
            if i == 0:
                i += 1
                continue
            cmark[date] = np.percentile(list(cma.loc[date]), 30)
            amark[date] = np.percentile(list(cma.loc[date]), 70)
            if cmark[date] == 0:
                amark[date] = amark[date]/2
        mark3 = {}
        mark3['cmark'] = cmark
        mark3['amark'] = amark
        return mark3

    # 计算回报率
    def return_ratio(self,str):
        if str == 'stk':
            return ((self.stk/self.stk.shift(1))-1).dropna()
        if str == 'mrk':
            return ((self.mrk / self.mrk.shift(1)) - 1).dropna()

    # 计算SMB因子和HML因子
    def get_SMB_HML(self,rr,btm,median,mark):
        smb = pd.Series(index=self.index_date,dtype='float64',name='smb')
        hml = pd.Series(index=self.index_date, dtype='float64',name='hml')
        i = 0
        for date in self.index_date:
            if i == 0:
                i += 1
                smb[date]=0
                hml[date]=0
                continue
            small_size = 0.0
            big_size = 0.0
            value_btm = 0.0
            growth_btm = 0.0
            for stk in self.stocks:
                if self.mrk_cap[stk][date] < median[date]:
                    num = rr[stk][date]*self.mrk_cap[stk][date]
                    small_size += num
                else:
                    big_size += rr[stk][date]*self.mrk_cap[stk][date]
                if btm[stk][date] < mark['lmark'][date]:
                    growth_btm += rr[stk][date]*self.mrk_cap[stk][date]
                if btm[stk][date] > mark['hmark'][date]:
                    value_btm += rr[stk][date]*self.mrk_cap[stk][date]

            mrkcap = np.sum(self.mrk_cap.loc[date])
            smb[date] = (small_size-big_size)/mrkcap
            hml[date] = (growth_btm-value_btm)/mrkcap
        return smb[1:],hml[1:]

    def get_RMW_CMA(self,rr,rmw,cma,mark2,mark3):
        rmw_ = pd.Series(index=self.index_date, dtype='float64', name='rmw')
        cma_ = pd.Series(index=self.index_date, dtype='float64', name='cma')
        i = 0
        for date in self.index_date:
            if i == 0:
                i += 1
                rmw[date] = 0
                cma[date] = 0
                continue
            r = 0.0
            w = 0.0
            c = 0.0
            a = 0.0
            for stk in self.stocks:
                if rmw[stk][date] < mark2['rmark'][date]:
                    num = rr[stk][date] * self.mrk_cap[stk][date]
                    r += num
                if rmw[stk][date] < mark2['wmark'][date]:
                        num = rr[stk][date] * self.mrk_cap[stk][date]
                        w += num
                if cma[stk][date] < mark3['cmark'][date]:
                    c += rr[stk][date] * self.mrk_cap[stk][date]
                if cma[stk][date] > mark3['amark'][date]:
                    a += rr[stk][date] * self.mrk_cap[stk][date]

            mrkcap = np.sum(self.mrk_cap.loc[date])
            rmw_[date] = (r - w) / mrkcap
            cma_[date] = (c - a) / mrkcap
        return rmw_[1:], cma_[1:]

    # 查看当前所有的股票
    def get_stock_list(self):
        df = pd.read_csv('data.csv')
        stock = []
        stock_list = df.columns.values.tolist()[2:]
        for s in stock_list:
            stock.append(int(s[:-6]))
        print(stock)
        return stock


    # FF3因素回归，传入某只股票的代码，获得相应的alpha与beta
    def FF3(self,stk_code):
        btm = self.get_btm()
        meadin = self.s_m_b()
        mark = self.h_m_l(btm)
        rr1 = self.return_ratio('stk')
        smb, hml = self.get_SMB_HML(rr1,btm,meadin,mark)
        rr2 = self.return_ratio('mrk')[1:]

        # 将所选股票的回报率作为y
        y = np.array(rr1[f'{stk_code}_close']-self.rf)[1:]
        Y = y.T

        #市场回报率，smb, hml作为X
        X = np.column_stack((rr2-self.rf,smb[1:],hml[1:]))
        X = sm.add_constant(X)

        mod = regression.linear_model.OLS(Y,X).fit()
        paras = mod.params
        names = ['alpha','beta','smb_p','hml_p']
        return dict(zip(names,paras))

    def FF5(self,stk_code):
        btm = self.get_btm()
        meadin = self.s_m_b()
        mark = self.h_m_l(btm)
        rr1 = self.return_ratio('stk')
        smb, hml = self.get_SMB_HML(rr1,btm,meadin,mark)

        rr2 = self.return_ratio('mrk')[1:]
        rmw = self.get_rmw()
        cma = self.get_cma()
        rr = self.return_ratio('stk')
        mark2 = self.r_m_w(rmw)
        mark3 = self.c_m_a(cma)
        rmw, cma = self.get_RMW_CMA(rr,rmw,cma,mark2,mark3)

        # 将所选股票的股价作为y
        y = np.array(rr1[f'{stk_code}_close']-self.rf)[1:]
        Y = y.T
        print(Y)

        #市场回报率, smb, hml, rwm, cma作为X, 股价作为Y进行线性回归
        #由于数据是随机生成的，因此重复执行会出现不同结果
        X = np.column_stack((rr2-self.rf,smb[1:],hml[1:],rmw[1:],cma[1:]))
        X = sm.add_constant(X)
        mod = regression.linear_model.OLS(Y,X).fit()
        paras = mod.params
        names = ['alpha','beta','smb_p','hml_p','rwm_p','cma_p']
        return dict(zip(names,paras))




f = FF_model('2020-11-22', '2021-12-7')

#获取能够使用类的股票代码
stocks = f.get_stock_list()
rr_3 = []
rr_5 = []
paras3 = f.FF3(600000)
paras5 = f.FF5(600000)





