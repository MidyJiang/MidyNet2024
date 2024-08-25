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
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "max-age=0",
    "Cookie": "optimizelyEndUserId=oeu1717674659120r0.09236825877804367; _gac_UA-22148828-10=1.1717674660.CjwKCAjwvIWzBhAlEiwAHHWgvROqcCcuYHTtmfwpLPNCtlCsw8ecW2ExVq6K-Crv-QRzzST1pUcB4RoCp4oQAvD_BwE; _gcl_aw=GCL.1717674660.CjwKCAjwvIWzBhAlEiwAHHWgvROqcCcuYHTtmfwpLPNCtlCsw8ecW2ExVq6K-Crv-QRzzST1pUcB4RoCp4oQAvD_BwE; _gcl_dc=GCL.1717674660.CjwKCAjwvIWzBhAlEiwAHHWgvROqcCcuYHTtmfwpLPNCtlCsw8ecW2ExVq6K-Crv-QRzzST1pUcB4RoCp4oQAvD_BwE; _gcl_gs=2.1.k1$i1717674659; _gcl_au=1.1.1187769271.1717674660; _ga_NTY0HBYF35=GS1.2.1717674659.1.0.1717674659.0.0.0; spoor-id=clx3755oq0000358fv4lvn0np; FTCookieConsentGDPR=true; FTClientSessionId=ae1f792f-3c9c-4da8-af21-7667e207aac5; _csrf=_zgBgyBfcv-0rOKRo5bl_F6m; o-typography-fonts-loaded=1; _cb=Dm-RAJBp5Xe5DM6FiV; __exponea_etc__=954f366a-dfc1-4b8b-a8ea-2874b092804b; __exponea_time2__=-1.1788792610168457; consentUUID=d9409b2e-e8d0-42c0-9452-92ea8cbf72ad_32; consentDate=2024-06-06T11:52:09.944Z; FTSession_s=01tjOTeWTUhe05P7vPseUMIz0wAAAY_uhLCWw8I.MEQCIDhCKUObBbi8t9VkbaY-RRQ0xzqWAdQgJrpimUJUdcEpAiAF9nrSLnU-h5_TS66XwGfUUGD2SCRUyF8AS8yUAMRgpw; FTConsent=behaviouraladsOnsite%3Aon%2CcookiesOnsite%3Aon%2CcookiesUseraccept%3Aoff%2CdemographicadsOnsite%3Aon%2CenhancementByemail%3Aoff%2CenhancementByfax%3Aoff%2CenhancementByphonecall%3Aoff%2CenhancementBypost%3Aoff%2CenhancementBysms%3Aoff%2CmarketingByemail%3Aoff%2CmarketingByfax%3Aoff%2CmarketingByphonecall%3Aoff%2CmarketingBypost%3Aoff%2CmarketingBysms%3Aoff%2CmembergetmemberByemail%3Aoff%2CpermutiveadsOnsite%3Aon%2CpersonalisedmarketingOnsite%3Aon%2CprogrammaticadsOnsite%3Aon%2CrecommendedcontentOnsite%3Aon; FTAllocation=5b633937-964d-485e-93fb-bcfb1e50c233; liveagent_oref=https://www.ft.com/; liveagent_sid=42240ffc-dd00-4b3e-9fe2-cc1004d8d183; liveagent_vc=2; liveagent_ptid=42240ffc-dd00-4b3e-9fe2-cc1004d8d183; _sp_id.4680=c3498c7b-d222-41fb-b978-8af3e2526e2b.1717694848.1.1717694848.1717694848.8f0c2952-b42a-4f1b-844a-3bb05c72d760; _ga=GA1.1.300139752.1717674660; _ga_12QH5VHXS4=GS1.1.1717694847.1.0.1717694855.0.0.244802451; _clck=8maf9g%7C2%7Cfmg%7C0%7C1618; ft-access-decision-policy=SUBSCRIPTION_POLICY; zit.data.toexclude=0; _sxh=1315,; permutive-id=d5c9b936-26f0-4072-9c42-472676b86187; _chartbeat2=.1717674729206.1717839165555.101.DQk3X7Bq36sUCJrbaKfOXsjCRJc9l.1; _cb_svref=external; _uetsid=34b70270257211ef86a1a1b7f6c21beb; _uetvid=3467571023fb11efb07acd60973c15de; sessionId=3384573; _sanba=-3; _sf=1; _sxo={\"R\":1,\"tP\":0,\"tM\":0,\"sP\":1,\"sM\":0,\"dP\":5,\"dM\":0,\"dS\":2,\"tS\":0,\"cPs\":1,\"lPs\":[0,30,1,1,10],\"sSr\":10,\"sWids\":[],\"wN\":0,\"cdT\":0,\"F\":1,\"RF\":1,\"w\":0,\"SFreq\":2,\"last_wid\":0,\"bid\":1036,\"accNo\":\"\",\"clientId\":\"\",\"isEmailAud\":0,\"isPanelAud\":0,\"hDW\":0,\"isRegAud\":0,\"isExAud\":0,\"isDropoff\":0,\"devT\":0,\"exPW\":0,\"Nba\":3,\"userName\":\"\",\"dataLayer\":\"\",\"localSt\":\"\",\"emailId\":\"\",\"emailTag\":\"\",\"subTag\":\"\",\"lVd\":\"2024-6-8\",\"oS\":\"D240608Kg1qi0L1AQ9Qz5sP06NICmWZZr6sCWtsnW5a5cpVrvc=\",\"cPu\":\"https://www.ft.com/content/ce8a6602-dece-4313-b1a5-4e6f3354f99d\",\"pspv\":4,\"pslv\":3384573,\"pssSr\":32,\"pswN\":0,\"psdS\":1,\"pscdT\":-3384535,\"RP\":0,\"TPrice\":0,\"ML\":\"\",\"isReCaptchaOn\":false,\"reCaptchaSiteKey\":\"\",\"reCaptchaSecretKey\":\"\",\"extRefer\":\"\",\"dM2\":0,\"tM2\":0,\"sM2\":0,\"RA\":0,\"ToBlock\":-1,\"CC\":\"GB\",\"groupName\":\"Journey A DNT\"}; _clsk=cujebd%7C1717839869769%7C14%7C0%7Cp.clarity.ms%2Fcollect",
    "If-None-Match": "W/\"22bf5-WpTlEUKYwYMwHxKjZ5S9lK5P4qQ\"",
    "Priority": "u=0, i",
    "Sec-Ch-Ua": "\"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "\"Windows\"",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
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