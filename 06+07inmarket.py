import time
import warnings
from datetime import datetime, timedelta
import os
import torch
import torch.nn.functional as F

import config
from module import MidyNet

warnings.filterwarnings('ignore')
"""
Load data: Load the data of each company.
Model prediction: Use the model to predict the probability of each stock rising or falling on each trading day.
Calculate score: Calculate the score of each stock (probability of rising - probability of falling).
Build investment portfolio: Select top K to go long and bottom K to go short.
Calculate return rate: Consider transaction costs and calculate the annualized return rate of the investment portfolio.
"""
print('\n', time.ctime())

flags = config.args
def yield_return_plot(period):
    import os
    import pandas as pd
    device = flags.device
    labels = flags.labels
    start = datetime.strptime(eval(f"flags.{period}_yield_start_date"), '%Y-%m-%d')
    end = datetime.strptime(eval(f"flags.{period}_yield_end_date"), '%Y-%m-%d')
    date_list = [start + timedelta(days=i) for i in range((end - start).days + 1)]
    filenames = os.listdir(flags.data_dir)
    company_list = [file.split(".")[0] for file in filenames]
    result = pd.DataFrame(index=date_list, columns=company_list)

    # load trained model
    with open("exp_name_temp.txt","r") as f:
        exp_name=f.read()
    model_path= f'{exp_name}.pt'
    model = MidyNet(flags)
    state_dict = torch.load(model_path)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()

    def daily_predict(x_test,day, ticker, flags,model):
            # conduct predictions
            with torch.no_grad():  # no grad while predicting
                y_pred_logits = model(x_test)  # get logits output
                y_pred = torch.argmax(y_pred_logits, dim=1).cpu().numpy()  # get labels
            y_pred_probs = F.softmax(y_pred_logits, dim=1)  # get probabilities
            predicted_label = labels[y_pred.item()]
            score = y_pred_probs.cpu().numpy()[0][1] - y_pred_probs.cpu().numpy()[0][2] #- y_pred_probs.cpu().numpy()[0][0]
            result[ticker][day] = score
            # print(f"Probabilities: {y_pred_probs}\t result={y_pred.item()},【{predicted_label}】: {score}")

    for ticker_count, ticker in enumerate(company_list):
        print(f"{ticker_count:<2}/{len(company_list)},\t{ticker}", end='\t')
        try:
            x_read = pd.read_csv(f'myft/tokenized/{ticker}/tokenized_all_x.csv', index_col=0, header=None)
            date_x = [i.split(" + ")[1] for i in x_read.index.tolist()]
            for day_count, day in enumerate(date_list):
                day = day.strftime('%Y-%m-%d')
                progress = f"{day_count + 1}/{len(date_list)}"
                print(f"\r{ticker_count:<4}/{len(company_list)},\t{ticker:<5}\t{progress}", end='')
                if day in date_x:
                    x_read.index = date_x
                    x_test = torch.tensor(
                        x_read.loc[day].values.reshape(-1, flags.days, flags.max_num_text_len, 3, flags.max_num_tokens_len),
                        dtype=torch.int64).to(device)
                    daily_predict(x_test,day, ticker, config.args,model)
                else: continue;
        except Exception as E:
            print(E)
            continue;
        print()
        # result.to_csv(f"{exp_name}_{period}_result.csv")

    result.to_csv(f"{exp_name}_{period}_result.csv")
    print('\n', time.ctime())
    print()
    import pandas as pd
    import numpy as np
    import os
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
    with open("exp_name_temp.txt","r") as f:
        exp_name=f.read()

    df = pd.read_csv(f"{exp_name}_{period}_result.csv", index_col=0)

    def select_top_bottom_k_stocks(df, K):
        # top K and bottom K
        top_k_stocks = df.apply(lambda row: row.nlargest(K).dropna().index.tolist(), axis=1)
        bottom_k_stocks = df.apply(lambda row: row.nsmallest(K).dropna().index.tolist(), axis=1)
        return top_k_stocks, bottom_k_stocks

    def Annualized_yield(K, transaction_cost):

        top_k_stocks, bottom_k_stocks = select_top_bottom_k_stocks(df, K)

        # get price data
        for _, _, prices_csv in os.walk("price/raw"):
            continue
        close_list = [pd.read_csv(os.path.join("price/raw", csv), index_col=0, usecols=['Date', 'Adj Close']).rename(
            columns={"Adj Close": csv.split(".csv")[0]}) for csv in prices_csv]
        price_data = pd.concat(close_list, axis=1)
        price_data.index = pd.to_datetime(price_data.index)  # format

        # daily return of portfolio
        def calculate_portfolio_returns(top_k_stocks, bottom_k_stocks, price_data, transaction_cost):
            daily_returns = []
            previous_top_portfolio = []
            previous_bottom_portfolio = []
            previous_prices = None

            for date, top_stocks in top_k_stocks.items():
                if date in price_data.index:
                    current_top_prices = price_data.loc[date, top_stocks].dropna()
                    current_bottom_prices = price_data.loc[date, bottom_k_stocks.get(date, [])].dropna()

                    # skip if first day (no previous day)
                    if previous_prices is None:
                        previous_prices = (current_top_prices, current_bottom_prices)
                        previous_top_portfolio = top_stocks
                        previous_bottom_portfolio = bottom_k_stocks.get(date, [])
                        continue

                    # daily return of current day
                    top_returns = current_top_prices / previous_prices[0] - 1
                    bottom_returns = current_bottom_prices / previous_prices[1] - 1
                    top_returns = top_returns.dropna()
                    bottom_returns = bottom_returns.dropna()

                    # consider transaction cost
                    top_transaction_costs = len(set(top_stocks) ^ set(previous_top_portfolio)) * transaction_cost
                    bottom_transaction_costs = len(
                        set(bottom_k_stocks.get(date, [])) ^ set(previous_bottom_portfolio)) * transaction_cost

                    # clarify daily return
                    if not top_returns.empty and not bottom_returns.empty:
                        portfolio_return = top_returns.mean() - bottom_returns.mean() - top_transaction_costs - bottom_transaction_costs
                        daily_returns.append(portfolio_return)

                    # update price and portfolio
                    previous_prices = (current_top_prices, current_bottom_prices)
                    previous_top_portfolio = top_stocks
                    previous_bottom_portfolio = bottom_k_stocks.get(date, [])

            return daily_returns

        daily_returns = calculate_portfolio_returns(top_k_stocks, bottom_k_stocks, price_data, transaction_cost)

        # daily return to annualized return
        def calculate_annualized_return(daily_returns):
            if not daily_returns:
                return np.nan
            avg_daily_return = np.mean(daily_returns)
            annualized_return = (1 + avg_daily_return) ** 252 - 1  # 252 trading day per year
            return annualized_return

        annualized_return = calculate_annualized_return(daily_returns)

        print(f"K={K:<4},comission%={transaction_cost:<7},Annualized Return: {annualized_return * 100:.2f}%")
        return annualized_return

    return_list = []
    for K in range(1, 20):
        transaction_cost = 1e-4
        return_list.append(Annualized_yield(K=K, transaction_cost=transaction_cost))
    plt.bar(range(len(return_list)),return_list,label=f'MidyNet_{exp_name}')
    plt.grid()
    plt.title(f"Annualized Return for {model} during {period.upper()} Period")
    plt.xlabel("K")
    plt.legend()
    plt.ylabel("Annualized Return (%)")
    def to_percent(temp, position):    return '%1.0f' % (100 * temp) + '%'
    plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent))
    plt.savefig(f"{exp_name}_{period}.png")
    # plt.show()
    plt.close()


for period in ['fall', 'rise', 'volatility', 'all']:
    yield_return_plot(period)

print('\n', time.ctime())