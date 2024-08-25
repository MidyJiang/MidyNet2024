import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from matplotlib.ticker import FuncFormatter
import warnings

warnings.filterwarnings('ignore')
import config

flags = config.args

with open("exp_name_temp.txt", "r") as f:
    exp_name = f.read()
model_map = dict(zip([exp_name, 'LSTM', 'GRU'], ['MidyNet', 'LSTM', 'GRU']))


def sharp_return(model, period):
    if model in ["SVM", "LSTM", "GRU"]:
        read_path = (f"D:\\UoS-inUK\\OneDrive - University of Southampton\\Semester "
                     f"2\\6563-dissertation\\DstPrep\\week06-Comparison\\{model}\\{period}_result.csv")
    else:
        read_path = f"{model}_{period}_result.csv"
    start_date = pd.to_datetime(eval(f"flags.{period}_yield_start_date"))
    end_date = pd.to_datetime(eval(f"flags.{period}_yield_end_date"))
    print(start_date, end_date, end='\t')
    try:
        df = pd.read_csv(read_path, index_col=0, parse_dates=True).loc[start_date:end_date]
    except Exception as e:
        print(read_path)
    df = df.fillna(-1).tail(30)

    def to_percent(temp, position):
        return '%1.0f' % (100 * temp) + '%'

    def calculate_sharpe_ratio(weights, scores):
        """
        Calculate the Sharpe ratio of a portfolio
        :param weights: portfolio weights
        :param scores: model prediction scores for each stock
        :return: Sharpe ratio (negative values are used for minimization)
        """
        portfolio_return = np.sum(scores.mean() * weights)
        portfolio_std = np.sqrt(np.dot(weights.T, np.dot(scores.cov(), weights)))
        sharpe_ratio = portfolio_return / portfolio_std
        return -sharpe_ratio  # negative for minimization

    def get_optimal_weights(scores):
        """
        get optimized portfolio weights
        :param scores: score for each ticker
        :return: optimized weights
        """
        num_assets = len(scores.columns)
        args = (scores,)
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x)})
        bound = (-1.0, 2.0)
        bounds = tuple(bound for asset in range(num_assets))
        result = minimize(calculate_sharpe_ratio, num_assets * [1. / num_assets, ], args=args,
                          method="SLSQP", bounds=bounds, constraints=constraints)  #
        return result.x

    # optimized weights
    optimal_weights = get_optimal_weights(df)

    # daily expected return
    portfolio_returns = df.dot(optimal_weights)

    # cumulative return
    cumulative_returns = (1 + portfolio_returns).cumprod() / 100

    # max drawdown
    cumulative_max = cumulative_returns.cummax()
    drawdown = (cumulative_returns - cumulative_max) / cumulative_max

    return_dict[model] = cumulative_returns
    drawdown_dict[model] = drawdown
    ax[0].plot(cumulative_returns, label=f"{model_map[model]}")
    print(f"{period:<10}{model:<7}Max Return={cumulative_returns.max()}\tMax drawdown={drawdown.min()}")
    ax[0].set_title(f'Cumulative Returns of Optimized Portfolio during {period} Period')
    ax[0].set_xlabel('Date')
    ax[0].set_ylabel('Cumulative Returns (%)')
    ax[0].legend()
    ax[0].grid(axis="x")
    ax[0].yaxis.set_major_formatter(FuncFormatter(to_percent))
    for tick in ax[0].get_xticklabels():
        tick.set_rotation(30)

    # plot max drawdown
    ax[1].plot(drawdown, label=f"{model_map[model]} Max Drawdown={drawdown.min():.2e}")
    ax[1].set_title(f'Max Drawdown during {period.upper()}')
    ax[1].set_xlabel('Date')
    ax[1].set_ylabel('Drawdown (%)')
    ax[1].legend()
    ax[1].grid(axis="y")
    # ax[1].yaxis.set_major_formatter(FuncFormatter(to_percent))

    plt.xticks(rotation=30)
    plt.tight_layout()


for period in ['fall', 'rise', 'volatility', 'all']:
    return_dict, drawdown_dict = {}, {}
    fig, ax = plt.subplots(1, 2, figsize=(14, 6))
    for model in [exp_name, 'LSTM', 'GRU']:
        sharp_return(model, period)
    pd.DataFrame(return_dict).to_csv(f"result/09-{period}-cumu_yield.csv")
    pd.DataFrame(drawdown_dict).to_csv(f"result/09-{period}-max_draw.csv")
    plt.xticks(rotation=30)
    plt.legend()
    plt.savefig(f"ALL_dual_{period}.png", dpi=800)
    print(f"ALL_dual_{period}.png,saved")
    plt.close()
    # plt.show()
