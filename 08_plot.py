import random, time

import pandas as pd
import numpy as np
import os, config
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# parameters

initial_funds = 1000000  # initial funds
transaction_cost_min = .1
transaction_cost_max = 5 # limitations
transaction_cost_rate = 0.0001
K_range = 10
K_step = 1
flags = config.args
with open("exp_name_temp.txt", "r") as f:
    exp_name = f.read()
# global variables
model_map = dict(zip([exp_name, 'LSTM', 'GRU'], ['MidyNet', 'LSTM', 'GRU']))
result_dict = {}


def select_top_bottom_k_stocks(model, df, K):
    if model == "SVM":
        top_k_stocks = df.apply(
            lambda row: row[row == 1].sample(n=min(K, (row == 1).sum()), random_state=flags.seed).index.tolist(),
            axis=1)
        bottom_k_stocks = df.apply(
            lambda row: row[row == 2].sample(n=min(K, (row == 2).sum()), random_state=flags.seed).index.tolist(),
            axis=1)
    else:
        top_k_stocks = df.apply(lambda row: row.nlargest(K).dropna().index.tolist(), axis=1)
        bottom_k_stocks = df.apply(lambda row: row.nsmallest(K).dropna().index.tolist(), axis=1)
    return top_k_stocks, bottom_k_stocks


def Annualized_yield(model, df, K, transaction_cost):
    top_k_stocks, bottom_k_stocks = select_top_bottom_k_stocks(model, df, K)

    # get price data
    for _, _, prices_csv in os.walk("price/raw"):
        continue
    close_list = [pd.read_csv(os.path.join("price/raw", csv), index_col=0, usecols=['Date', 'Close']).rename(
        columns={"Close": csv.split(".csv")[0]}) for csv in prices_csv]
    price_data = pd.concat(close_list, axis=1)
    price_data.index = pd.to_datetime(price_data.index)

    # portfolio daily return
    def calculate_portfolio_returns(top_k_stocks, bottom_k_stocks, price_data, transaction_cost):
        daily_returns = []
        previous_top_portfolio = []
        previous_bottom_portfolio = []
        previous_prices = None

        for date, top_stocks in top_k_stocks.items():
            if date in price_data.index:
                current_top_prices = price_data.loc[date, top_stocks].dropna()
                current_bottom_prices = price_data.loc[date, bottom_k_stocks.get(date, [])].dropna()

                # skip if day 1
                if previous_prices is None:
                    previous_prices = (current_top_prices, current_bottom_prices)
                    previous_top_portfolio = top_stocks
                    previous_bottom_portfolio = bottom_k_stocks.get(date, [])
                    continue

                # daily return
                top_returns = current_top_prices / previous_prices[0] - 1
                bottom_returns = current_bottom_prices / previous_prices[1] - 1
                top_returns = top_returns.dropna()
                bottom_returns = bottom_returns.dropna()

                # transaction cost
                top_transaction_costs = len(set(top_stocks) ^ set(previous_top_portfolio)) * transaction_cost
                bottom_transaction_costs = len(
                    set(bottom_k_stocks.get(date, [])) ^ set(previous_bottom_portfolio)) * transaction_cost

                if not top_returns.empty and not bottom_returns.empty:
                    portfolio_return = top_returns.mean() - bottom_returns.mean() - top_transaction_costs - bottom_transaction_costs
                    daily_returns.append(portfolio_return)

                # update
                previous_prices = (current_top_prices, current_bottom_prices)
                previous_top_portfolio = top_stocks
                previous_bottom_portfolio = bottom_k_stocks.get(date, [])

        return daily_returns

    daily_returns = calculate_portfolio_returns(top_k_stocks, bottom_k_stocks, price_data, transaction_cost)

    # annualized return
    def calculate_annualized_return(daily_returns):
        if not daily_returns:
            return np.nan
        avg_daily_return = np.mean(daily_returns)
        annualized_return = (1 + avg_daily_return) ** 252 - 1  # 252 trading day per year
        return annualized_return

    annualized_return = calculate_annualized_return(daily_returns)

    print(f"K={K:<4},comission%={transaction_cost:<7},Annualized Return: {annualized_return * 100:.2f}%")
    return annualized_return


def to_percent(temp, position):
    return '%1.0f' % (100 * temp) + '%'


def annual_return(model):
    result_dict[model] = []
    if model in ["SVM", "LSTM", "GRU"]:
        read_path = (f"D:\\UoS-inUK\\OneDrive - University of Southampton\\Semester "
                     f"2\\6563-dissertation\\DstPrep\\week06-Comparison\\{model}\\{period}_result.csv")
    else:
        read_path = f"{exp_name}_{period}_result.csv"
    df = pd.read_csv(read_path, index_col=0)
    for K in range(2, K_range, K_step):
        result_dict[model].append(Annualized_yield(model, df, K, transaction_cost_rate))


def plot_return(labels, data, tick_step=1, group_gap=0.2, bar_gap=0.0, period='rise'):
    x = np.arange(len(labels)) * tick_step
    group_num = len(data)
    group_width = tick_step - group_gap
    bar_span = group_width / group_num
    bar_width = bar_span - bar_gap

    plt.figure(figsize=(7,6))
    for index, y in enumerate(data):
        bars = plt.bar(x + index * bar_span, y, bar_width, label=model_map[model_list[index]])
        for bar in bars:
            if bar.get_height() < 0:
                bar.set_edgecolor('red')
                bar.set_linestyle((0, (1, 1)))
                # bar.set_linewidth(2)
                bar.set_alpha(.7)

    plt.legend()
    plt.grid(axis='y')
    plt.xlabel("K")
    plt.ylabel("Annualized Return (%)")
    ticks = x + (group_width - bar_span) / 2
    plt.xticks(ticks, labels)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent))
    plt.title(f"Annualized Return for Different Methods during {period} Period")

    pd.DataFrame(data, index=model_list, columns=np.arange(2, K_range, K_step)).to_csv(f"result/08-{period}Yield.csv")
    plt.savefig(f"ALL-{period}.png",dpi=800)
    print(f"ALL-{period}.png saved。")
    plt.close()


model_list = [exp_name, 'LSTM', 'GRU']

for period in ['fall', 'rise', 'volatility', 'all']:
    try:
        for model in model_list:
            annual_return(model)
        data = [result_dict[model] for model in model_list]
        plot_return(np.arange(2, K_range, K_step), data, bar_gap=0.0, period=period)
    except:
        continue;
# plt.show()

print('\n', time.ctime())
