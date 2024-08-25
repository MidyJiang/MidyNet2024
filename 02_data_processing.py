import json
import pandas as pd
import os,time,traceback

print('\n',time.ctime())#estimate time: 375 hrs

top30 = pd.read_csv('all115.csv', index_col=0)

for _, _, csv_list in os.walk('myft/scrapped'):
    # try:
    for company_csv in csv_list:
        name = company_csv[company_csv.find("_") + 1:company_csv.find(".csv")]
        ticker = top30[top30['Company Name'] == name].Symbol.values[0]
        print(f"{company_csv:<40}", end='\t')
        df = pd.read_csv(os.path.join('myft/scrapped', company_csv)).iloc[:, 1:].dropna(subset=['time']).reset_index(drop=True)

        # Create a set of unique dates
        date_dict = {pd.to_datetime(df['time'].iloc[i]).strftime("%Y-%m-%d") for i in range(len(df)) if pd.notnull(df['time'].iloc[i])}

        for date in date_dict:
            data = [{"text": df.title[i],"created_at": pd.to_datetime(df[['time']].iloc[i].values[0]).strftime("%Y-%m-%d %H:%M:%S")}
                    for i in range(len(df)) if
                    pd.to_datetime(df[['time']].iloc[i].values[0]).strftime("%Y-%m-%d") == date]
            # print(f"data:{data}")
            ### unsplitted consistent text: raw to json
            os.makedirs(f'myft/raw/{ticker}', exist_ok=True)
            json.dump(data, open(f'myft/raw/{ticker}/{date}.json', 'w'))

            ### split and save: preprocessed to txt

            tokenized_data = []  # tokenized result
            for item in data:  # tokenize and formalize
                tokenized_data.append({'text': item['text'].split(" "), 'created_at': item['created_at']})
            os.makedirs(f'myft/preprocessed/{ticker}', exist_ok=True)
            with open(f'myft/preprocessed/{ticker}/{date}', 'w') as f:
                for item in tokenized_data:
                    f.write(json.dumps(item) + '\n')
        print(ticker)
    # except:
    #     traceback.print_exc()
    #     break;
print('\n',time.ctime())
