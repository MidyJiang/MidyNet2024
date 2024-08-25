import time
from datetime import date, datetime, timedelta
import json
import numpy as np
import os
import pandas as pd
from transformers import AutoTokenizer
from pathlib import Path
import config
import time

args = config.args

print('\n', time.ctime())
# filenames = os.listdir(args.data_dir)
# print(filenames)
# stock_name_price = set([filename.split('.')[0] for filename in filenames])
filenames = os.listdir(args.data_dir)
stock_name_price = set([filename.rsplit('.', 1)[0] for filename in filenames])
#########################

stock_name_news = set(os.listdir(args.news_dir))
stock_names = set.intersection(stock_name_news, stock_name_price)
print(f"stock names list: {stock_names}")
start = datetime.strptime(args.train_start_date, '%Y-%m-%d')
end = datetime.strptime(args.test_end_date, '%Y-%m-%d')

date_list = [start + timedelta(days=i) for i in range((end - start).days + 1)]
y = pd.DataFrame(index=date_list, columns=list(stock_names))

for filename in filenames:
    stock_name = filename.split(".")[0]
    if stock_name not in stock_names:
        continue

    filepath = args.data_dir + filename
    df = pd.read_csv(filepath, header=None, index_col=0, parse_dates=True, sep='\t')
    for index, move_per in zip(df.index, df[1]):
        y[stock_name][index] = move_per

y[y > 0.0055] = 1                           # rise
y[(-0.005 <= y) & (y <= 0.0055)] = 0        # preserve
y[y < -0.005] = 2                           # fall

BERT_tokenizer = AutoTokenizer.from_pretrained(args.modelpath)
news_data = dict()  #(key: stock_name + date, value: tokenized_news)
for stock_name in stock_names:
    print(stock_name + ' token')
    file_names = os.listdir(args.news_dir + stock_name)
    for file_name in file_names:
        file_path = args.news_dir + stock_name + '/' + file_name
        key = stock_name + ' + ' + file_name
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            jsons = [json.loads(line) for line in lines]

            text_data = [' '.join(jsons[i]['text']) if i < len(jsons) else '' for i in range(args.max_num_text_len)]
            tokens = BERT_tokenizer(text_data,
                                    max_length=args.max_num_tokens_len,
                                    truncation=True,
                                    padding='max_length',
                                    )  # input_ids(20, 30), token_type_ids(20, 30), attension_mask(20, 30)
            news_data[key] = tokens

train_x = pd.DataFrame()
train_y = pd.DataFrame()
dev_x = pd.DataFrame()
dev_y = pd.DataFrame()
test_x = pd.DataFrame()
test_y = pd.DataFrame()

train_start_date = datetime.strptime(args.train_start_date, '%Y-%m-%d')
train_end_date = datetime.strptime(args.train_end_date, '%Y-%m-%d')
dev_start_date = datetime.strptime(args.dev_start_date, '%Y-%m-%d')
dev_end_date = datetime.strptime(args.dev_end_date, '%Y-%m-%d')
test_start_date = datetime.strptime(args.test_start_date, '%Y-%m-%d')
test_end_date = datetime.strptime(args.test_end_date, '%Y-%m-%d')

train_idx = 0
dev_idx = 0
test_idx = 0
num_filtered_samples = 0

for ticker_count, stock_name in enumerate(stock_names):  # for every ticker
    ticker_count += 1
    per_train_x, per_test_x, per_dev_x = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    per_train_y, per_test_y, per_dev_y = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    per_save_path = os.path.join(args.per_save_path, stock_name)
    os.makedirs(per_save_path, exist_ok=True)

    sample = np.zeros((args.days, args.max_num_text_len, 3, args.max_num_tokens_len))
    # inaitialize a sample with size=(days, max_num_text_len, 3, max_num_tokens_len)
    print(f"{ticker_count:<5},{stock_name:<9}", end='\t')  # current ticker
    for target_date in date_list:  # for every date loop
        if y[stock_name][target_date] not in (0, 1, 2):  # if not proper in (0,1,2) skip
            continue
        num_no_news_days = 0  # counter of none-news-date
        for lag in range(args.days + 1, 1, -1):  #  reverse loop from (days + 1) to day No.2
            news_date = target_date - timedelta(days=lag)  # lag day before target date
            key = stock_name + ' + ' + str(news_date.date())  # generate key for news data
            if key in news_data:
                news_ids = news_data[key]
                sample[args.days - lag, :, 0, :] = np.array(news_ids['input_ids'])
                sample[args.days - lag, :, 1, :] = np.array(news_ids['token_type_ids'])
                sample[args.days - lag, :, 2, :] = np.array(news_ids['attention_mask'])
            else:
                num_no_news_days += 1  # add on none-news-date counter
                if num_no_news_days > 5:  # consistent counter nore than 5 days
                    break

        if num_no_news_days > 5:
            num_filtered_samples += 1  # add a filter
            continue

        label = y[stock_name][target_date] # get label for current ticker and date

        if train_start_date <= target_date <= train_end_date:
            train_x = pd.concat([train_x, pd.DataFrame(np.expand_dims(np.ravel(sample), axis=0), index=[key])])
            train_y = pd.concat([train_y, pd.DataFrame([label], index=[key])])
            per_train_x = pd.concat([per_train_x, pd.DataFrame(np.expand_dims(np.ravel(sample), axis=0), index=[key])])
            per_train_y = pd.concat([per_train_y, pd.DataFrame([label], index=[key])])
        elif dev_start_date <= target_date <= dev_end_date:
            dev_x = pd.concat([dev_x, pd.DataFrame(np.expand_dims(np.ravel(sample), axis=0), index=[key])])
            dev_y = pd.concat([dev_y, pd.DataFrame([label], index=[key])])
            per_dev_x = pd.concat([per_dev_x, pd.DataFrame(np.expand_dims(np.ravel(sample), axis=0), index=[key])])
            per_dev_y = pd.concat([per_dev_y, pd.DataFrame([label], index=[key])])
        elif test_start_date <= target_date <= test_end_date:
            test_x = pd.concat([test_x, pd.DataFrame(np.expand_dims(np.ravel(sample), axis=0), index=[key])])
            test_y = pd.concat([test_y, pd.DataFrame([label], index=[key])])
            per_test_x = pd.concat([per_test_x, pd.DataFrame(np.expand_dims(np.ravel(sample), axis=0), index=[key])])
            per_test_y = pd.concat([per_test_y, pd.DataFrame([label], index=[key])])

    print(
        f"train:{per_train_x.shape}{per_train_y.shape},\tdev:{per_dev_x.shape}{per_dev_y.shape},\ttest{per_test_x.shape}{per_test_y.shape}",
        end=' ')
    per_train_x.to_csv(f"{per_save_path}//train_x.csv", header=False)
    per_train_y.to_csv(f"{per_save_path}//train_y.csv", header=False)
    per_dev_x.to_csv(f"{per_save_path}/dev_x.csv", header=False)
    per_dev_y.to_csv(f"{per_save_path}/dev_y.csv", header=False)
    per_test_x.to_csv(f"{per_save_path}/test_x.csv", header=False)
    per_test_y.to_csv(f"{per_save_path}/test_y.csv", header=False)
    x_tokenized_per_ticker = pd.concat([per_train_x, per_dev_x, per_test_x])
    y_tokenized_per_ticker = pd.concat([per_train_y, per_dev_y, per_test_y])
    print(f"tknzd all:{x_tokenized_per_ticker.shape}{y_tokenized_per_ticker.shape}")
    x_tokenized_per_ticker.to_csv(f"{per_save_path}//tokenized_all_x.csv", header=False)
    y_tokenized_per_ticker.to_csv(f"{per_save_path}//tokenized_all_y.csv", header=False)

save_path = args.dataset_save_dir
dir = Path(save_path)
dir.mkdir(parents=True, exist_ok=True)

print("dataset de shapes:", train_x.shape, train_y.shape, dev_x.shape, dev_y.shape, test_x.shape, test_y.shape, )

train_x.to_csv(save_path + 'train_x.csv', header=False)
train_y.to_csv(save_path + 'train_y.csv', header=False)
dev_x.to_csv(save_path + 'dev_x.csv', header=False)
dev_y.to_csv(save_path + 'dev_y.csv', header=False)
test_x.to_csv(save_path + 'test_x.csv', header=False)
test_y.to_csv(save_path + 'test_y.csv', header=False)

print('\n', time.ctime())
