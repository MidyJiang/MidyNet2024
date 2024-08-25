import argparse

argparser = argparse.ArgumentParser()
# https://github.com/BigRoddy/CMIN-Dataset/tree/main/CMIN-US
argparser.add_argument('--data_dir', type=str, default='price/preprocessed/')
argparser.add_argument('--news_dir', type=str, default='myft/preprocessed/')
argparser.add_argument('--dataset_save_dir', type=str, default='dataset/')
argparser.add_argument('--per_save_path', type=str, default='myft/tokenized/')

# 05:trainng
argparser.add_argument('--learning_rate', type=float, default=1e-4)
argparser.add_argument('--weight_decay', type=float, default=1e-4)
argparser.add_argument('--batch_size', type=int, default=64)
argparser.add_argument('--dr', type=float, default=0.3)  # dropout rate
argparser.add_argument('--hidden_size', type=int, default=20)
argparser.add_argument('--train_epochs', type=int, default=10)
argparser.add_argument('--check_interval', type=int, default=1)
argparser.add_argument('--device', type=str, default='cuda')
argparser.add_argument('--usewb', type=bool, default=True)
argparser.add_argument('--save_dir', type=str, default='wandb')
argparser.add_argument('--num_workers', type=int, default=0)
argparser.add_argument('--CHECKPOINT_PATH', type=str, default='checkpoint/')
argparser.add_argument('--optimizer', type=str, default='adamw')
argparser.add_argument('--freeze', type=bool, default=True)
argparser.add_argument('--modelpath', type=str, default='yiyanghkust/finbert-pretrain')

# 04/05:dataset and loader
argparser.add_argument('--num_class', type=int, default=3)
argparser.add_argument('--labels', type=dict, default=dict(zip([0,1,2],[ "preserve", "rise", "fall"])))
argparser.add_argument('--days', type=int, default=5)
argparser.add_argument('--max_num_text_len', type=int, default=10) #max news for each day
argparser.add_argument('--max_num_tokens_len', type=int, default=30)
argparser.add_argument('--seed', type=int, default=34518509)



argparser.add_argument('--train_start_date', type=str, default='2010-01-01')
argparser.add_argument('--train_end_date', type=str, default='2018-09-24')
argparser.add_argument('--dev_start_date', type=str, default='2018-09-25')
argparser.add_argument('--dev_end_date', type=str, default='2023-02-04')
argparser.add_argument('--test_start_date', type=str, default='2023-02-05')
argparser.add_argument('--test_end_date', type=str, default='2024-07-20')

# VOLATILITY
argparser.add_argument('--volatility_yield_start_date', type=str, default='2019-06-10')
argparser.add_argument('--volatility_yield_end_date', type=str, default='2019-06-29')
# RISE
argparser.add_argument('--rise_yield_start_date', type=str, default='2020-12-01')
argparser.add_argument('--rise_yield_end_date', type=str, default='2020-12-15')
# FALL
argparser.add_argument('--fall_yield_start_date', type=str, default='2023-06-01')
argparser.add_argument('--fall_yield_end_date', type=str, default='2024-01-01')

#ALL
argparser.add_argument('--all_yield_start_date', type=str, default='2010-01-01')
argparser.add_argument('--all_yield_end_date', type=str,  default='2024-07-20')

# from datetime import datetime, timedelta
# start_date, end_date = datetime.strptime("2010-01-01", '%Y-%m-%d'), datetime.strptime("2024-07-20", '%Y-%m-%d')
# total_days = (end_date - start_date).days + 1
# train_days, dev_days, test_days = total_days * .6, total_days *.3, total_days *.1
# train_end_date = start_date + timedelta(days=train_days - 1)
# dev_start_date, dev_end_date = train_end_date + timedelta(days=1), train_end_date + timedelta(days=dev_days)
# test_start_date, test_end_date = dev_end_date + timedelta(days=1), dev_end_date + timedelta(days=test_days)
# print(f"argparser.add_argument('--train_start_date', type=str, default='{start_date.strftime('%Y-%m-%d')}')")
# print(f"argparser.add_argument('--train_end_date', type=str, default='{train_end_date.strftime('%Y-%m-%d')}')")
# print(f"argparser.add_argument('--dev_start_date', type=str, default='{dev_start_date.strftime('%Y-%m-%d')}')")
# print(f"argparser.add_argument('--dev_end_date', type=str, default='{dev_end_date.strftime('%Y-%m-%d')}')")
# print(f"argparser.add_argument('--test_start_date', type=str, default='{test_start_date.strftime('%Y-%m-%d')}')")
# print(f"argparser.add_argument('--test_end_date', type=str, default='{test_end_date.strftime('%Y-%m-%d')}')")

argparser.add_argument('--train_x_path', type=str, default='dataset/train_x.csv')
argparser.add_argument('--train_y_path', type=str, default='dataset/train_y.csv')
argparser.add_argument('--dev_x_path', type=str, default='dataset/dev_x.csv')
argparser.add_argument('--dev_y_path', type=str, default='dataset/dev_y.csv')
argparser.add_argument('--test_x_path', type=str, default='dataset/test_x.csv')
argparser.add_argument('--test_y_path', type=str, default='dataset/test_y.csv')

args = argparser.parse_args(args=[])
