from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from alpaca_trade_api import REST
from datetime import datetime
from timedelta import Timedelta 
from fin_bert_utils import estimate_sentiment_batch
from dotenv import load_dotenv
import os 
import certifi
from flask import Flask, request
from multiprocessing import Process
from datetime import datetime
from flask import request

app = Flask(__name__)

load_dotenv()
os.environ["SSL_CERT_FILE"] = certifi.where()

BASE_URL_LUMIBOT = os.getenv("BASE_URL_LUMIBOT")


ALPACA_CREDS = {
    "API_KEY": os.getenv("API_KEY_LUMIBOT"),
    "API_SECRET": os.getenv("API_SECRET_LUMIBOT"),
    "PAPER": True
}

class MLTrader(Strategy):
    """
    A machine learning-based trading strategy.

    Attributes:
        symbol_ticker (str): The symbol of the asset to trade.
        sleeptime (str): The sleep time between trading iterations.
        last_trade (str): The type of the last trade made ('buy' or 'sell').
        cash_at_risk (float): The percentage of cash to risk per trade.
        _benchmark_asset (str): The symbol of the benchmark asset.
        api (REST): The REST API object for making API calls.

    Methods:
        initialize(): Initializes the strategy.
        on_trading_iteration(): Executes the trading logic on each trading iteration.
        position_sizing(): Calculates the position size based on available cash and asset price.
        get_dates(): Retrieves the current date and the date three days prior.
        get_sentiment(): Retrieves the sentiment and probability of the asset based on news headlines.
    """
    def initialize(self):
        self.symbol_ticker = self.parameters['symbol']
        self.sleeptime = "24H"
        self.last_trade = None
        self.cash_at_risk = self.parameters['cash_at_risk']
        self._benchmark_asset = self.parameters['benchmark_asset']
        self.api = REST(base_url=BASE_URL_LUMIBOT, key_id=ALPACA_CREDS["API_KEY"], secret_key=ALPACA_CREDS["API_SECRET"])
    
    def on_trading_iteration(self):
        cash, last_price, quantity = self.position_sizing()
        prob, sentiment = self.get_sentiment()
        if cash > last_price: 
            if sentiment == "positive" and prob > .999:
                if self.last_trade == 'sell':
                    self.sell_all()
                order  = self.create_order(
                    self.symbol_ticker,
                    quantity, "buy", type="bracket",
                    take_profit_price=last_price*1.20,
                    stop_loss_price=last_price*.95
                )
                self.submit_order(order)
                self.last_trade = 'buy'
            elif sentiment == "negative" and prob > .999:    
                if self.last_trade == 'buy':
                    self.sell_all()
                order  = self.create_order(
                    self.symbol_ticker,
                    quantity, "sell", type="bracket",
                    take_profit_price=last_price*0.8,
                    stop_loss_price=last_price*1.05
                )
                self.submit_order(order)
                self.last_trade = 'sell'
        
    def position_sizing(self):
        cash = self.get_cash()
        last_price = self.get_last_price(self.symbol_ticker) 
        quantity = round(cash*self.cash_at_risk / last_price, 2) #number of shares to buy/sell
        return cash , last_price, quantity
    
    def get_dates(self):
        today = self.get_datetime()
        three_days_prior = today - Timedelta(days=3)
        return today.strftime("%Y-%m-%d"),  three_days_prior.strftime("%Y-%m-%d")
    
    def get_sentiment(self):
        today, three_days_prior = self.get_dates()
        news = self.api.get_news(self.symbol_ticker, start=three_days_prior, end=today)
        news  = [ev.__dict__['_raw']['headline'] for ev in news]
        prob, sentiment  = estimate_sentiment_batch(news)
        return prob, sentiment

# start_date = datetime(2023,12,1)
# end_date = datetime(2024,2,6)


def backtest(start_date:datetime, end_date:datetime, ticker, cash_at_risk, benchmark_asset, budget):
    broker = Alpaca(ALPACA_CREDS)
    statergy  = MLTrader(name ="mlstrat" ,broker = broker)
    statergy.backtest(
        YahooDataBacktesting, start_date, end_date,
        show_plot=True,
        show_tearsheet=True,
        budget=budget,
        parameters={"symbol": ticker, "cash_at_risk": cash_at_risk, "benchmark_asset": benchmark_asset}
        )

@app.route('/backtest', methods=['POST'])
def handle_backtest():
    data = request.json
    print(data)
    start_date = datetime.strptime(data['start_date'], "%Y-%m-%d")
    end_date = datetime.strptime(data['end_date'], "%Y-%m-%d")
    ticker = str(data['ticker'])
    cash_at_risk = float(data['cash_at_risk'])
    benchmark_asset = str(data['benchmark_asset'])
    budget = float(data['budget'])
    print(start_date, end_date, ticker, cash_at_risk, benchmark_asset, budget)
    p = Process(target=backtest, args=(start_date, end_date, ticker, cash_at_risk, benchmark_asset, budget))
    p.start()
    p.join()
    return {"success": "Backtest completed successfully"}
    


if __name__ == '__main__':
    app.run(port=5000)




# backtest(start_date, end_date, "SPY", .5, "SPY")

