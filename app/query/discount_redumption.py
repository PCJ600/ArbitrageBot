# 折价套利策略

g_fund_redemption_rates = {
    '501305': 0.001,
    '501306': 0.001,
    '501307': 0.001,
    '164705': 0,
    '501310': 0.005,
    '501301': 0.005,
    '501302': 0.005,
    '160924': 0.005,
    '160717': 0.005,
    '161831': 0.005
}

# 判断fund_id对应的LOF基金是否有折价套利的可能
def is_discount_arbitrage_possible(fund_id, discount_rate):
    # 溢价基金没法做折价套利
    if discount_rate > 0:
        return False

    # 不在自选池的基金不做折价套利
    if fund_id not in g_fund_redemption_rates:
        return False

    # 实时折价率扣除赎回费后有0.7%的利润空间, 可以套利
    cost = g_fund_redemption_rates.get(fund_id)
    return abs(discount_rate) - cost > 0.006


if __name__ == "__main__":
    print(is_discount_arbitrage_possible('501305', -0.02)) # expected: True
    print(is_discount_arbitrage_possible('501305', -0.01)) # expected: False

