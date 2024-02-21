from duckduckgo_search import DDGS

from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from llama_index.query_engine import PandasQueryEngine
from llama_index.vector_stores.types import ExactMatchFilter, MetadataFilters
from llama_index.tools import QueryEngineTool, ToolMetadata, FunctionTool
from llama_index.query_engine import PandasQueryEngine

from pydantic import BaseModel, Field
from llama_index import VectorStoreIndex
import pandas as pd
from config import (MODEL_NAME, astra_db_store, NUM_RESULTS_FROM_DDG, 
                    EARNINGS_CONTEXT, STOCKS_CONTEXT, BALANCE_SHEET_CONTEXT, 
                    INCOME_STATEMENT_CONTEXT, quater_map)

from fin_bert_utils import estimate_sentiment_single

class extract(BaseModel):
    """
    Given the query extract quarter of the year
    """
    quarter: str = Field(default="Q4", description='''The quarter of the earnings from quarter choices: 
                        ['Q1', 'Q2', 'Q3', 'Q4']  also accepts  ['First', 'Second', 'Third', 'Fourth'] 
                        also accepts ['1', '2', '3', '4'] also accepts
                         ['first', 'second', 'third', 'fourth'] if nothing return Fourth''')

def extract_year_quater(query):
    print(query)
    model = ChatOpenAI(model=MODEL_NAME)
    parser = PydanticOutputParser(pydantic_object=extract)
    prompt = PromptTemplate(
        template= "Extract the quarter from the given query.\n{query}\n{format_instructions}",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    chain = prompt | model | parser

    resp = chain.invoke({"query": query})
    return resp.quarter

def load_csv(ticker_df):
    engine = PandasQueryEngine(df=ticker_df, verbose=True, streaming=True)
    return engine

def get_index(ticker:str, quarter:str="Q4"):
    '''
    Retrieves the relevant index from Astra based on the provided ticker, year, and quarter.

    Args:
        ticker (str): The ticker symbol of the stock.
        year (str): The year of the earnings report.
        quarter (str): The quarter of the earnings report.

    Returns:
        md_query_engine: The query engine for the relevant index.

    Raises:
        Exception: If the index is not found.
    '''
    print(ticker, quarter)
    try:
        md_index = VectorStoreIndex.from_vector_store(vector_store = astra_db_store)
        md_query_engine = md_index.as_query_engine(
            filters=MetadataFilters(
                filters=[ExactMatchFilter(key="Ticker", value=ticker), ExactMatchFilter(key="Quarter", value= quater_map[quarter])]
            ),
            similarity_top_k=5
        )
        return md_query_engine
    except:
        print(f'Index not found________________________________')



def get_balance_sheet(ticker):
    df = pd.read_csv(f"balance_sheet/balanceSheetStatement-{ticker}-annual.csv")
    engine = PandasQueryEngine(df=df, verbose=True, synthesize_response=True)
    return engine

def get_income_statement(ticker):
    df = pd.read_csv(f"income_statement/incomeStatement-{ticker}-annual.csv")
    engine = PandasQueryEngine(df=df, verbose=True, synthesize_response=True)
    return engine

def get_cashflow(ticker):
    df = pd.read_csv(f"cash_flow_statement/cashflowStatement-{ticker}-annual.csv")
    engine = PandasQueryEngine(df=df, verbose=True, ynthesize_response=True)
    return engine



def ddg_news(search:str, ticker:str) ->list:
    """
    Fetches news articles from DuckDuckGo search based on the given keywords and the stock ticker.
    Along with the sentiment of the news.

    Args:
        search (str): The keywords to search for.
        Stock (str): The stock ticker to search for.

    Returns:
        list: A list of news articles.

    """
    x = []
    with DDGS() as ddgs:
        keywords = search + " on stock" + ticker
        ddgs_news_gen = ddgs.news(
            keywords,
            region="wt-wt",
            safesearch="off",
            timelimit="m",
            max_results=NUM_RESULTS_FROM_DDG
        )
        for r in ddgs_news_gen:
            sentiment = estimate_sentiment_single(r['title']) 
            x.append("Title:- "+r['title']+ "\n" +"Whole news:- "+ r['body']+"\n" + "Sentiment:- "+ sentiment+ "\n")
    return "\n".join(x) 

def ddg_search(search: str, ticker: str)->list:
    """
    Fetches search results from DuckDuckGo based on the given keywords and the stock ticker.
    Last option to be used if no other tool is available.

    Args:
        search (str): The keywords to search for.

    Returns:
        list: A list of search results.

    """
    x = []
    with DDGS() as ddgs:
        keywords = search + " on stock" + ticker
        ddgs_search_gen = ddgs.text(
            keywords,
            timelimit="m",
            max_results=NUM_RESULTS_FROM_DDG,
        )
        for r in ddgs_search_gen:
            x.append(r['title'] + "\n" + r['body'])
    return "\n".join(x)


def get_engine_tools(ticker, quarter, ticker_df):
    """
    Get a list of query engine tools.

    Args:
        ticker (str): The ticker symbol.
        quarter (str): The quarter.
        ticker_df (pandas.DataFrame): The ticker dataframe.

    Returns:
        list: A list of QueryEngineTool objects.
    """
    query_engine_tools = [
        QueryEngineTool(
            query_engine=get_index(ticker, quarter),
            metadata=ToolMetadata(
                name="earnings",
                description=(EARNINGS_CONTEXT),
            ),
        ),
        QueryEngineTool(
            query_engine=load_csv(ticker_df),
            metadata=ToolMetadata(
                name="stocks",
                description=(STOCKS_CONTEXT),
            ),
        ),
        QueryEngineTool(
            query_engine=get_balance_sheet(ticker),
            metadata=ToolMetadata(
                name="balance_sheet",
                description=(BALANCE_SHEET_CONTEXT),
            ),
        ),
        QueryEngineTool(
            query_engine=get_income_statement(ticker),
            metadata=ToolMetadata(
                name="income_statement",
                description=(INCOME_STATEMENT_CONTEXT),
            ),
        ),
        FunctionTool.from_defaults(fn=ddg_news, async_fn=True),
        FunctionTool.from_defaults(fn=ddg_search, async_fn=True),
    ]
    return query_engine_tools
