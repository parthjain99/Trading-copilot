from dotenv import load_dotenv  
import os
from llama_index.vector_stores import AstraDBVectorStore

load_dotenv()


ASTRA_DB_APPLICATION_TOKEN = os.environ.get("ASTRA_DB_APPLICATION_TOKEN")
ASTRA_DB_API_ENDPOINT = os.environ.get("ASTRA_DB_API_ENDPOINT")
ASTRA_DB_NAME = os.getenv("ASTRA_DB_NAME")  
astra_db_store = AstraDBVectorStore(
    token=ASTRA_DB_APPLICATION_TOKEN,
    api_endpoint=ASTRA_DB_API_ENDPOINT,
    collection_name=ASTRA_DB_NAME,
    embedding_dimension=1536,
)

quater_map =  {
    "Q1": "Q1",
    "Q2": "Q2",
    "Q3": "Q3",
    "Q4": "Q4",
    "1": "Q1",
    "2": "Q2",
    "3": "Q3",
    "4": "Q4",
    "first": "Q1",
    "second": "Q2",
    "third": "Q3",
    "fourth": "Q4",
    'First': 'Q1',
    'Second': 'Q2',
    'Third': 'Q3',
    'Fourth': "Q4"
}
stock_options = ('QCOM', 'ABNB', 'GOOG', 'AMD', 'NFLX', 'META', 'AAPL', 'NVDA', "INTC", 'TSLA', 'ADP', 'AMZN', 'COST', 'PYPL')


NUM_RESULTS_FROM_DDG = 5

MODEL_NAME = "gpt-3.5-turbo-0613"
MAX_ITERATIONS = 13
REACT_CONTEXT = '''
You are a stock market sorcerer who is an expert on the companies listed on the stock market.\
You will answer questions about these companies as in the persona of a sorcerer.
and veteran stock market investor. Use the tools and generally follow a Chain of thought to answer the questions and 
try to break the question frame better so that can be found. KEEP final response concise and to the point.\
'''
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

EARNINGS_CONTEXT = '''
    A query engine that can answer qualitative questions about a set of SEC financial documents that 
    the user pre-selected for the conversation. Any questions about company-related headwinds, tailwinds, 
    risks, sentiments, or administrative information, company-related earnings should be asked here. 
    generally what would work is the query as input in plaintext.
'''

# STOCKS_CONTEXT = '''Provides information about stockprices (past and present) of the company. 
# The csv is already loaded in dataframe. Use a Pandas query to return the output. the dataframe 
# is already loaded in the tool.'''

STOCKS_CONTEXT = """
This context provides a structured framework for querying stock price information from a pre-loaded 
Pandas DataFrame. Key columns in this DataFrame include 'Date', 'Open', 'Close', 'High', 'Low'.
You dont need to pass Company tickers as that data is already loaded in the tool according to the query.
Give inputs as Plain text (Should understandable and easily converted to query) and the tool will convert 
it to a pandas query and return the output.Your task is to utilize Pandas querying capabilities 
to extract specific insights from the 'stock_prices' DataFrame. 
Perform operations such as filtering for particular dates or companies, calculating statistical 
summaries (e.g., average, maximum, minimum), and analyzing trends over specified periods. 
"""

BALANCE_SHEET_CONTEXT = '''Provides information about balance sheet (last 5 years 2019-2023) 
of the company. The csv is already loaded in dataframe. The year is in calendarYear use that to fiter on year.
Try to give the full query in one go , Give inputs as Plain text and the tool will convert it to a pandas query and return the output.
Your task is to utilize Pandas querying capabilities 
to extract specific insights from the 'stock_prices' DataFrame. 
'''

INCOME_STATEMENT_CONTEXT = '''Provides information about income statement (last 5 years 2019-2023) 
of the company. The csv is already loaded in dataframe.The year is in calendarYear use that to fiter on year.and Try to give the full queryin one go.
Give inputs as Plain text and the tool will convert it to a pandas query and return the output.
to extract specific insights from the 'stock_prices' DataFrame. 
'''


CHATBOT_HELLO ="""Hello, I'm your Trading Co-Pilot, here to empower your investment decisions with timely and insightful data. 
                Here's what I can do for you:
                \n Stock Prices: Ask for real-time or historical stock prices.
                \n Earnings Reports: Get detailed quarterly or annual earnings reports for any company.
                \n News Sentiment: Understand the sentiment behind the latest stock-related news.
                \n Financial Statements: Access comprehensive balance and income statements from recent years.
                \n Market Analysis: Receive updates and analyses on the latest market news.
                \n Internet Queries: Query the internet for stock information, including investor sentiments and analyst ratings.
                \n Leverage these features to make informed decisions and stay ahead in the market.
"""

AUTO_REFRESH_INTERVAL  = 5*60*1000
