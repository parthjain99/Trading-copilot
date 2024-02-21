import requests
import pandas as pd
import xml.etree.ElementTree as ET
import os

headers = {'User-Agent': 'parthjain9925@gmail.com'}
ticker_cik = requests.get('https://www.sec.gov/files/company_tickers.json', headers=headers)  
ticker_cik =  pd.json_normalize(pd.json_normalize(ticker_cik.json(),max_level=0).values[0])
ticker_cik['cik_str'] = ticker_cik['cik_str'].astype(str).str.zfill(10)


def give_cik(ticker):
  return ticker_cik[ticker_cik['ticker'] == ticker]['cik_str'].values[0]

def request_reportdata(cik):
  return requests.get(f'https://data.sec.gov/rss?cik={cik}&type=10-K,10-Q,10-KT,10-QT,NT%2010-K,NT%2010-Q,NTN%2010K,NTN%2010Q&count=40', headers = headers)

def XML_to_DF(cik):
# Parse the XML data
    df = pd.DataFrame()
    root = ET.fromstring(request_reportdata(cik).content)

    # Find all the entry elements
    entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')

    # Print each entry
    for entry in entries:
        if df.empty:
            df = pd.read_xml(ET.tostring(entry, encoding='unicode'))
        else:
            df= pd.concat([df, pd.read_xml(ET.tostring(entry, encoding='unicode'))], ignore_index = True)
    return df

def give_report_date(cik, access_num, date_strings_fixed, ticker):
    num = 4
    for i in range(len(date_strings_fixed)):
        url = f'https://www.sec.gov/Archives/edgar/data/{cik}/{access_num[i]}/{ticker.lower()}-{date_strings_fixed[i]}.htm'
        r = requests.get(url = url, headers = headers).content
        # with open(f'Q{num}.html', 'wb') as f:
        with open(f'content/{ticker}-Q{num}-2023.html', 'wb') as f:
            f.write(r)
        num-=1

if __name__ == '__main__':
    tickers = set(['AZN', 'BKR', 'AVGO', 'BIIB', 'BKNG', 'CDNS', 'ADBE', 'CHTR', 'CPRT', 
                'CSGP', 'CRWD', 'CTAS', 'CSCO', 'CMCSA', 'COST', 'CSX', 'CTSH', 'DDOG',
                'DXCM', 'FANG', 'DLTR', 'EA', 'ON', 'EXC', 'TTD', 'FAST', 'GFS',
                'META', 'FI', 'FTNT', 'GILD', 'GOOG', 'GOOGL', 'HON', 'ILMN',
                'INTC', 'INTU', 'ISRG', 'MRVL', 'IDXX', 'KDP', 'KLAC', 'KHC',
                'LRCX', 'LULU', 'MELI', 'MAR', 'MCHP', 'MDLZ', 'MRNA', 'MNST',
                'MSFT', 'MU', 'NFLX', 'NVDA', 'NXPI', 'ODFL', 'ORLY', 'PCAR',
                'PANW', 'PAYX', 'PDD', 'PYPL', 'PEP', 'QCOM', 'REGN', 'ROST',
                'SIRI', 'SBUX', 'SNPS', 'TSLA', 'TXN', 'TMUS', 'VRSK', 'VRTX',
                'WBA', 'WBD', 'WDAY', 'XEL', 'ZS', 'ADP', 'ABNB', 'AMD', 'CEG',
                'AMZN', 'AMGN', 'AEP', 'CDW', 'CCEP', 'ADI', 'MDB', 'DASH', 'ROP',
                'ANSS', 'SPLK', 'AAPL', 'AMAT', 'GEHC', 'ASML', 'TEAM', 'ADSK'])
    print(len(tickers))
    ticks = tickers.copy()
    for ticker in tickers:
        cik = give_cik(ticker)
        df_xml_parse = XML_to_DF(cik)
        if df_xml_parse.empty:
            ticks.remove(ticker)
            continue
        df_report_date = list(df_xml_parse.dropna(subset=['report-date'])['report-date'])
        df_accession_num = list(df_xml_parse.dropna(subset=['report-date'])['accession-number'])
        acess_num = [x.replace('-', '') for x in df_accession_num]
        date_strings_fixed = [x.replace('-', '') for x in df_report_date]
        give_report_date(cik, acess_num, date_strings_fixed, ticker)
    # ticks = {'CSGP', 'CEG', 'MU', 'CTSH', 'PEP', 'PYPL', 'TMUS', 'ISRG', 'CSCO', 
    #          'AMD', 'ADSK', 'FAST', 'ILMN', 'CPRT', 'CHTR', 'KHC', 'BKNG', 'MDB', 
    #          'META', 'ABNB', 'FANG', 'PCAR', 'EA', 'AVGO', 'MDLZ', 'ORLY', 'FI', 
    #          'GEHC', 'GOOGL', 'REGN', 'ADBE', 'BKR', 'KLAC', 'LULU', 'PAYX', 'XEL',
    #          'SPLK', 'AEP', 'ROST', 'QCOM', 'EXC', 'BIIB', 'LRCX', 'MSFT', 'GILD', 
    #          'CMCSA', 'VRSK', 'IDXX', 'DDOG', 'AMAT', 'TXN', 'INTU', 'SNPS', 'CTAS', 
    #          'DXCM', 'MRNA', 'VRTX', 'ANSS', 'COST', 'ZS', 'FTNT', 'ODFL', 'CRWD', 
    #          'ADI', 'AAPL', 'AMGN', 'MCHP', 'CSX', 'CDW', 'SBUX', 'MAR', 'DLTR', 
    #          'NXPI', 'GOOG', 'KDP', 'TSLA', 'NFLX', 'NVDA', 'INTC', 'TEAM', 'MRVL', 
    #          'ADP', 'WDAY', 'TTD', 'CDNS', 'ROP', 'MNST', 'PANW', 'HON', 'WBD', 'MELI', 
    #          'AMZN', 'WBA', 'DASH', 'ON', 'SIRI'}
    print(len(ticks))

