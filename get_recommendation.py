import os
from alpaca_trade_api import REST
from timedelta import Timedelta 
from fin_bert_utils import estimate_sentiment_batch
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()

BASE_URL_LUMIBOT = os.getenv("BASE_URL_LUMIBOT")


ALPACA_CREDS = {
    "API_KEY": os.getenv("API_KEY_LUMIBOT"),
    "API_SECRET": os.getenv("API_SECRET_LUMIBOT"),
    "PAPER": True
}
api = REST(base_url=BASE_URL_LUMIBOT, key_id=ALPACA_CREDS["API_KEY"], secret_key=ALPACA_CREDS["API_SECRET"])

def get_dates():
    today = datetime.today()
    three_days_prior = today - Timedelta(days=3)
    return today.strftime("%Y-%m-%d"),  three_days_prior.strftime("%Y-%m-%d")

def get_recommendation(symbol_ticker):
    """
    Get a recommendation (BUY, SELL, or No Strong Signal) based on the sentiment analysis of recent news articles.

    Parameters:
    symbol_ticker (str): The symbol or ticker of the stock.

    Returns:
    str: The recommendation (BUY, SELL, or No Strong Signal).
    """
    today, three_days_prior = get_dates()
    news = api.get_news(symbol_ticker, start=three_days_prior, end=today)
    news  = [ev.__dict__['_raw']['headline'] for ev in news]
    prob, sentiment  = estimate_sentiment_batch(news)
    if sentiment == "positive" and prob > .999:
        return f"BUY"
    elif sentiment == "negative" and prob > .999:    
       return'SELL'
    else:
        return 'No Strong Signal'


