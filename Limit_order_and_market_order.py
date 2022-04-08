from matplotlib import pyplot as plt

class online_trade:
    def __init__(self, bid, ask):#初始化市场情况
        self.bid = bid
        self.ask = ask
        self.stock_price = [min(ask)]

    def sell_limit(self, price, lots):#sell limit order处理
        price_list = self.ask.keys()
        if price in price_list:
            self.ask[price] += lots
        else:
            self.ask[price] = lots
        print(f'挂单ask {price} {lots}手')
        self.stock_price.append(self.stock_price[-1])
        self.show_market()

    def buy_limit(self, price, lots):#buy limit order处理
        price_list = self.bid.keys()
        if price in price_list:
            self.bid[price] += lots
        else:
            self.bid[price] = lots
        print(f'挂单bid {price} {lots}手')
        self.stock_price.append(self.stock_price[-1])
        self.show_market()

    def sell_market(self, lots):#sell market order处理
        num = lots
        stock = sorted(list(self.bid.keys()),reverse=True)
        total = 0
        for lot in stock:
            total += self.bid[lot]
        if lots > total:
            print(f"市场无{lots}手需求")
        else:
            sell_list = []
            for price in stock:
                if self.bid[price] <= lots:
                    lots -= self.bid[price]
                    info = {'price':price, 'lots':self.bid[price]}
                    sell_list.append(info)
                    if lots == 0:
                        self.stock_price.append(price)
                        break
                    del self.bid[price]
                else:
                    self.stock_price.append(price)
                    self.bid[price] -= lots
                    info = {'price': price, 'lots': lots}
                    sell_list.append(info)
                    break
            print(f"卖出 {num}手信息：{sell_list}")
            self.show_market()

    def buy_market(self, lots):#buy market order处理
        num = lots
        stock = sorted(self.ask.keys())
        total = 0
        for lot in stock:
            total += self.ask[lot]
        if lots > total:
            print(f"市场无{lots}手供给")
        else:
            buy_list = []
            for price in stock:
                if self.ask[price] <= lots:
                    lots -= self.ask[price]
                    info = {'price': price, 'lots': self.ask[price]}
                    buy_list.append(info)
                    if lots == 0:
                        self.stock_price.append(price)
                        break
                    del self.ask[price]
                else:
                    self.stock_price.append(price)
                    self.ask[price] -= lots
                    info = {'price': price, 'lots': lots}
                    buy_list.append(info)
                    break
            print(f"买入{num}手信息：{buy_list}")
            self.show_market()

    def get_wrong(self):#系统出错提醒，防止程序停止崩溃
        print('输入指令错误，请检查，或输入help查看指令')

    def get_help(self):#帮助用户使用指令
        print(f'''交易指令: instruction(buy or sell) type(limit or market) (if limit price(int)) lots(int)
退出指令: quit
显示市场: show''')

    def deal(self, word):#综合处理交易函数
        instruction = word[0]
        if instruction == 'sell':
            if len(word) == 3:
                self.sell_market(int(word[2]))
            elif len(word) == 4:
                self.sell_limit(float(word[2]), int(word[3]))
            else:
                raise Exception
        elif instruction == 'buy':
            if len(word) == 3:
                self.buy_market(int(word[2]))
            elif len(word) == 4:
                self.buy_limit(float(word[2]), int(word[3]))
            else:
                raise Exception
        else:
            raise Exception

    def show_market(self):#排序需求并展示市场需求
        print(f"ask: {dict(sorted(self.ask.items(), key=lambda data: data[0]))}")
        print(f"bid: {dict(sorted(self.bid.items(), key=lambda data: data[0], reverse=True))}")

    def show_stock(self):
        stock_price = self.stock_price
        n = len(stock_price)
        trade = [i for i in range(n)]
        plt.plot(trade, stock_price)
        plt.xlabel('trade times')
        plt.ylabel('stock price')
        plt.show()


    def emulation(self):#启动订单簿模拟的函数
        while True:
            word = input('输入仿真密钥: ')
            if word == 'start':
                self.show_market()
                while True:
                    try:
                        word = input('输入指令: ')
                        word = word.split()
                        if word[0] == 'help':
                            self.get_help()
                        elif word[0] == 'quit':
                            break
                        elif word[0] == 'show_price':
                            self.show_market()
                        elif word[0] == 'show_stock':
                            self.show_stock()
                        else:
                            self.deal(word)
                    except:
                        self.get_wrong()
                self.show_stock()
                break
            else:
                if word == 'quit':
                    break
                print('密钥错误，可重复输入，或输入quit退出')





