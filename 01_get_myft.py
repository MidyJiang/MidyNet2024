import w3lib.html
import requests
from requests_html import HTMLSession
import pandas as pd
import random, os, time
from bs4 import BeautifulSoup

import json

print('\n',time.ctime())
# account cookie
midy_headers = {
   # classified, should be drawn from repository secret
}

myft_url = r'https://www.ft.com/__myft/api/onsite/5b633937-964d-485e-93fb-bcfb1e50c233/followed/concept'
asession = HTMLSession()
response = asession.get(myft_url, headers=midy_headers)
while response.status_code != 200:  # loop till status_code=200
    print(f"【1.{response.status_code}】Retrying..", end='.')
    time.sleep(random.random() * 15)
    response = asession.get(myft_url, headers=midy_headers)

content = json.loads(BeautifulSoup(response.content, 'html.parser').text)

myft_df = pd.DataFrame(content['items'])[['name', 'uuid']]
myft_df['url'] = [f"https://www.ft.com/stream/{content['items'][i]['uuid']}" for i in range(len(myft_df))]

for j in range(len(myft_df)):  # j represents the number of each company
    time.sleep(random.random() * 3)
    page = 0
    result_df = pd.DataFrame()
    print(f"【{str(j).zfill(3)}】\t{myft_df['name'][j]}")
    while True:
        time.sleep(random.random() * 5)
        page += 1
        topic_url = f"{myft_df['url'][j]}?page={page}"
        each_topic = asession.get(topic_url, headers=midy_headers)  # go into company list
        if each_topic.status_code == 404 or each_topic.status_code == 400:
            print(f"【{str(j).zfill(3)}】\t{myft_df['name'][j]}\tresult={result_df.shape}【done.】\n")
            break
        print(topic_url)

        while each_topic.status_code != 200:  # loop till status_code=200
            print(f"【2.{each_topic.status_code}】Retrying..", end='.')
            time.sleep(random.random() * 15)
            each_topic = asession.get(topic_url, headers=midy_headers)

        for i, item in enumerate(each_topic.html.find("div.o-teaser--article")):  #every item in topic page
            each_dict = {}
            # each_dict['data-id']=item.attrs['data-id'],
            each_url = list(item.find("div.o-teaser__heading a")[0].absolute_links)[0]
            each_dict['url'] = each_url

            r = asession.get(each_url, headers=midy_headers)
            if r.status_code == 500:break;
            while r.status_code != 200: # loop till status_code=200
                print(f"【3.{r.status_code}】Retrying..")
                time.sleep(random.random() * 15)
                r = asession.get(each_url, headers=midy_headers)

            # bs4  parse html into json
            soup = BeautifulSoup(w3lib.html.remove_tags_with_content(r.text, which_ones=('aside',)), "html.parser")

            # title
            each_dict['title'] = soup.find_all("h1")[0].text
            # author
            try:
                author = soup.find_all(class_="n-content-tag--author")[0].text
            except:
                author = 'FT Review'
            each_dict['author'] = author
            try:
                # abstract
                each_dict['abstract'] = soup.find_all(class_="o-topper__standfirst")[0].text
                # publish time
                each_dict['time'] = pd.to_datetime(
                    soup.find_all(class_="article-info__timestamp o-date")[0].attrs['datetime'])
                # article content
                a = soup.find_all(attrs={"id": "article-body"})[0]
                each_content = a.text.replace("\n", "").replace("\"", "\"")
                each_dict['content'] = each_content
                each_dict['length'] = len(each_content)
            except:                print('error', each_url)
            each_dict['url'] = each_url

            result_df = pd.concat([result_df, pd.DataFrame(each_dict, index=[i])])

    result_df.to_csv(f"myft/scrapped/{str(j).zfill(3)}_{myft_df['name'][j]}.csv")

# print(myft_df['name'][22], result_df.shape)

print('\n',time.ctime())
