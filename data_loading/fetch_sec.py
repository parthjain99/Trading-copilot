import requests
import pandas as pd
import time
import matplotlib.pyplot as plt
import seaborn as sns
import ast
'''
The first thing to know is that the SEC indexes companies by a 10-digit Central Index Key (CIK) 
while the most common index used to search for a company’s data is its Ticker name.
'''
headers = {'User-Agent': 'parthjain9925@gmail.com'}
ticker_cik = requests.get('https://www.sec.gov/files/company_tickers.json', headers=headers)  
ticker_cik =  pd.json_normalize(pd.json_normalize(ticker_cik.json(),max_level=0).values[0])
ticker_cik['cik_str'] = ticker_cik['cik_str'].astype(str).str.zfill(10)
def EDGAR_q(cik:str, header:dict, tag:list=None):
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    response = requests.get(url, headers=header)
    if tag == None:
        tags = list(response.content.json()['facts']['us-gaap'].keys())
    else:
        tags = tag
    company_data = pd.DataFrame()
    for i in range(len(tags)):
        try:
            tag = tags[i]
            units = list(response.json()['facts']['us-gaap'][tag]['units'].keys())[0]
            data = pd.json_normalize(response.json()['facts']['us-gaap'][tag]['units'][units])
            data['tag'] = tag
            data['units'] = units
            company_data = pd.concat([company_data, data], ignore_index=True)
        except:
            print(tag + ' not found.')
    return company_data

EDGAR_data = pd.DataFrame()
for i in range(len(ticker_cik)):
    cik = ticker_cik['cik_str'][i]
    ticker = ticker_cik['ticker'][i]
    title = ticker_cik['title'][i]
    company_data = EDGAR_q(cik=cik, header = headers, tag=['RevenueFromContractWithCustomerExcludingAssessedTax'])
    company_data['cik'] = cik
    company_data['ticker'] = ticker
    company_data['title'] = title
    # Filter for quarterly data only
    try:
        company_data = company_data[company_data['frame'].str.contains('Q') == True] # Keep only quarterly data
    except:
        print('frame not a column.')
    EDGAR_data = pd.concat([EDGAR_data, company_data], ignore_index=True)
    print(i)
    time.sleep(0.1) # Be polite to the API

EDGAR_data.to_csv('EDGAR_data.csv')
EXPD_data = EDGAR_data[EDGAR_data[ticker] == 'EXPD'].copy()
EXPD_data['frame'] = EXPD_data['frame'].str.replace("CY", "")
EXPD_data['val _billions'] = EXPD_data['val']/1000000000
sns.set_theme(style='darkgrid')
fig = sns.lineplot(data=EXPD_data, x="frame", y='val_billions')
fig.set(xlabel='Quarter', ylabel='Revenue (billions USD)', title='EXPD')
plt.show()


