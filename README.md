# Trading-Copilot: Analyze, Ask, and Test

**Project Goal:**

Struggling to navigate the ever-changing stock market? Wish you had an AI-powered assistant by your side? Look no further! Introducing your new trading co-pilot, an innovative tool designed to empower you with insightful analysis, comprehensive information, and the ability to test your trading strategies.

**Uncover insights:** Dive deep into any stock of your choice. Analyze historical data, financial reports, and news articles to gain a comprehensive understanding of its performance and potential.

**Ask and be answered:** Curious about a company's future prospects? Unsure about the impact of recent news? Ask your co-pilot anything related to finance and receive clear, informative answers powered by advanced AI technology.

**Test your tactics:** Craft personalized trading strategies based on your own analysis and insights. Backtest them using historical data and sentiment analysis to assess their potential performance before entering the real market.

## Getting started

To get started with the project, follow these steps:

1. Create a virtual environment using

   `python3 -m venv myenv`.
2. Activate the virtual environment by running

   `source myenv/bin/activate`.
3. Install the required dependencies by running

   `pip install -r requirements.txt`.
4. Install the `alpaca-trade-api` package by running

   `pip install alpaca-trade-api`.
5. Install `pandas` version 1.5.3 by running

   `pip install pandas==1.5.3`.

## Running the Trading Bot

1. Open two terminals.
2. In one terminal, run the command

   `python3 trading_bot.py`.
3. In the other terminal, run the command

   `streamlit run app.py`.

Here is short video on how it works and looks. Testing questions pertaining to  different tools.

[Trading-Copilot Demo](https://www.youtube.com/watch?v=rVriypL9r5U)

Here is the architecture on what is happening around  stream-lit:

![1708548318194](image/README/1708548318194.png)


1. **Data Sources** : The system starts by sourcing financial data through the Yahoo Finance API, which provides historical stock prices and contemporary news articles relevant to the financial markets. This data is typically delivered in CSV format, offering a structured approach to historical stock price analysis. Concurrently, news articles are retrieved about the given stock.
2. **Sentiment Analysis** : The news headlines are processed by FinBERT, a pre-trained BERT model that has been fine-tuned on financial data to analyze sentiment. This sentiment analysis is used to gauge the market sentiment towards specific stock and then fed into trading bot for strategy, and also to stream-lit for prediction to buy and sell and to the stream-lit for single news sentiment.
3. **Trading Bot** : A trading bot, backed by Lumibot, uses the processed data to backtest trading strategies. Backtesting involves applying trading rules to historical data to determine the viability of a strategy.
4. **Query and Response System** : : The ReAct Agent, complemented by the Llama Index Query Engine, forms an interactive layer capable of processing user queries. Users can inquire about various financial data points and analyses, and the system responds with accurate information, drawing from its vast repository of indexed data.
