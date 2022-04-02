from Limit_order_and_market_order import online_trade
#默认仿真密钥为start
#指令例子： sell limit 1300.0 10; buy market 100


ask = {1300.05:100, 1300.04:30, 1300.03:20, 1300.02:10, 1300.01:5, 1300.00: 100}
bid = {1299.99:2, 1299.98:10, 1299.97:50, 1299.96:100, 1299.95:2}


test = online_trade(bid,ask)
test.emulation()
