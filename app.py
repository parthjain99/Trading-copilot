import streamlit as st
from streamlit_autorefresh import st_autorefresh

from datetime import datetime
from timedelta import Timedelta

import plotly.express as px

import yfinance as yf
from yahoo_fin import news
from yahoo_fin.stock_info import (get_live_price, get_quote_table)


from llama_index.agent import ReActAgent
from llama_index.agent import OpenAIAgent
from llama_index.llms import OpenAI

from dotenv import load_dotenv
import os
import warnings
import logging
import certifi
import json
import pandas as pd
from get_recommendation import get_recommendation
from fin_bert_utils import estimate_sentiment_single
import requests
import warnings
import logging
from config import (OPENAI_API_KEY,
                    stock_options,  MODEL_NAME, 
                    MAX_ITERATIONS, REACT_CONTEXT, CHATBOT_HELLO, AUTO_REFRESH_INTERVAL)

from utils import (extract_year_quater, 
                    get_engine_tools)

warnings.simplefilter(action="ignore", category=FutureWarning)
log = logging.getLogger(__name__)

os.environ["SSL_CERT_FILE"] = certifi.where()


@st.cache_resource
def setup_agent(ticker, quater, ticker_df):
    llm = OpenAI(model=MODEL_NAME)

    agent = ReActAgent.from_tools(
        get_engine_tools(ticker,quater, ticker_df),
        llm=llm,
        verbose=True,
        context=REACT_CONTEXT,
        max_iterations=MAX_ITERATIONS,
    )
    return agent

def string_to_generator(string):
  for char in string:
    yield char

# Convert the string to a generator object
def ask_chat(content, ticker_id, ticker_df):
    """
    Function to process user input and generate a chatbot response.

    Parameters:
    content (str): The user input.
    ticker_id (int): The ID of the ticker.
    ticker_df (pandas.DataFrame): The DataFrame containing ticker data.

    Returns:
    response (generator): The chatbot response.
    source (str): The source of the response.
    """
    if content:
        try:
            quater = extract_year_quater(content)
        except:
             quater = None, None
        if quater:
            agent = setup_agent(ticker_id, quater, ticker_df)
        else:
            agent = setup_agent(ticker_id, None, None, ticker_df)
        response = agent.chat(content)
        source = response.sources 
        response = string_to_generator(str(response.response))
    else:
        response = string_to_generator(CHATBOT_HELLO)
        source = ''
        
    return response, source

@st.cache_resource
def import_stock_data(tickerSymbol):
    ticker = yf.Ticker(tickerSymbol)
    end_date = datetime.now().strftime('%Y-%m-%d')
    tickerSymbol_df = ticker.history(start='2015-01-01',end=end_date)
    return tickerSymbol_df 

tab1, tab2 = st.tabs(["Traiding Copilot", "Backtest your Trading Strategy"])

# update every 5 mins
st_autorefresh(interval=AUTO_REFRESH_INTERVAL, key="dataframerefresh")

with tab1:
    with st.sidebar:
        option = st.selectbox(
        label = 'Select a stock Ticker?',
        options = stock_options, index=0)

        data = get_quote_table(ticker = option)
        keys_to_remove = ['Beta (5Y Monthly)', 'Bid', "Day's Range", 'Ex-Dividend Date', 
                            'Forward Dividend & Yield', 'Open', 'Quote Price','Avg. Volume']
        
        for key in keys_to_remove:
            data.pop(key, None)
        df = pd.DataFrame.from_dict(data, orient='index', columns=['Value'], dtype = str)
        with st.container(border=True):
            st.table(df)
        recommendation = get_recommendation(option)
        if recommendation == "BUY":
            new_recommend = f"<h3 style='color:#16F529;'>{recommendation}</h3>"
        elif recommendation == "SELL":
            new_recommend = f"<h3 style='color:red;'>{recommendation}</h3>"
        else:
            new_recommend = f"<h3>{recommendation}</h3>"
        st.write(f"<h3>Recommendation based on stratergy.: {new_recommend}</h3>", unsafe_allow_html=True)
        st.write(f"<h3>Latest News on {option} Stock<h3>", unsafe_allow_html=True)
        with st.container(border=True):
            news_101 = news.get_yf_rss(option)
            
            for i in range(len(news_101[:10])):
                with st.container(border=True):
                    sentiment  = estimate_sentiment_single(news_101[i]['title'])
                    if sentiment == 'negative':
                        st.write(f"<h4 style='color:red;'>{news_101[i]['title']}</h4>", unsafe_allow_html=True)
                    elif sentiment == 'positive':
                        st.write(f"<h4 style='color:#16F529;'>{news_101[i]['title']}</h4>", unsafe_allow_html=True)
                    else:
                        st.write(f"<h4>{news_101[i]['title']}</h4>", unsafe_allow_html=True)                
                    st.write(news_101[i]['summary'][:min(len(news_101[i]['summary']),100)]+f'''<a href ="{news_101[i]['link']}"> More</a>''', unsafe_allow_html=True)
                    formatted_date = datetime.strptime(news_101[i]['published'], '%a, %d %b %Y %H:%M:%S %z').strftime('%d, %b %Y %H:%M')
                    st.write(formatted_date)
        st.write(f'''<a href ="https://news.duckduckgo.com/?q={option}&iar=news&ia=news">More</a>''', 
                unsafe_allow_html = True)
    
    tickerSymbol_df = import_stock_data(option)

    if get_live_price(option) < tickerSymbol_df['Close'][-20]:
        new_title = f'<h3 style="color:red;">  {option}: {round(get_live_price(option),2)}</h3>'
    else:
        new_title = f'<h3 style="color:#16F529;"> {option}: {round(get_live_price(option),2)}</h3>'

    st.write(f"{new_title}", unsafe_allow_html=True)


    fig = px.line(tickerSymbol_df, x=tickerSymbol_df.index, y="Close",
            title=f'Closing Price of {option} Stock in (USD)') 

    st.plotly_chart(fig)


    # React to user input
    if prompt := st.chat_input(f"{option}: What would you like to know about this stock."):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        try:
            stream, source = ask_chat(prompt, option, tickerSymbol_df)
            response = st.write_stream(stream)
            with st.expander("View Source"):
                for i in range(len(source)):
                    st.write(f"Tool used {source[0].tool_name}")
                    st.write(f"Input {source[0].raw_input}")
                    # st.write(f"Input {source[0].raw_input['input']}")
                    st.write(f"Output {source[0].raw_output}")

        except Exception as e:
            response = st.write(f"Sorry, I'm unable to process your request at the moment. {e}")

with tab2:
    st.title('Backtest your Trading Strategy')
    with st.form(key='my_form'):
        col1, col2 = st.columns(2)
        with col1:
            stock_to_watch = st.text_input(label='Stock to watch/ Backtest', value=option)
            start_date = st.date_input(label='Start Date', value=datetime.today() - Timedelta(days=10), min_value=datetime(2020, 1, 1), max_value=datetime.today() - Timedelta(days=10))
            benchmark_asset = st.text_input(label='Benchmark Asset', value=option)
        with col2:
            budget = st.number_input(label='Budget', value=100000, min_value=0, step=1)
            end_date = st.date_input(label='End Date', value=datetime.today() - Timedelta(days=4), min_value=datetime(2020, 1, 1), max_value=datetime.today() - Timedelta(days=4))
            cash_risk = st.number_input(label='Cash Risk', value=0.5, min_value=0.0, max_value=1.0, format="%.2f", step=0.1)
        submit = st.form_submit_button(label="Backtest") 
        if submit and end_date - start_date <= Timedelta(days=3):
            st.error("start date should be less than end date by atleast 2 days", icon="🚨")
        elif submit:
            with st.spinner('Backtesting your strategy...'):
                url = "http://127.0.0.1:5000/backtest"  # Replace with the appropriate URL
                body = { 
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "ticker": stock_to_watch,
                    "cash_at_risk": cash_risk,
                    "benchmark_asset": benchmark_asset,
                    "budget": budget,
                }
                print(json.dumps(body))
                response = requests.post(url, data=json.dumps(body), headers={"Content-Type": "application/json"})
                response_json = response.json()
                st.write(response_json['success'])

# def main():
#     search = 'What is the investor sentiment on QCOM, Inc. over the last week according to internet sources?'
#     # print(ddg_news(search))

#     # with DDGS() as ddgs:
#     #     results = [r for r in ddgs.news("python programming", max_results=5)]
#     # print(results)

#     # q = extract_year_quater("Risk Factor of meta in Quarter 2?")
#     # print(q)
#     # md_query_engine = get_index("META", q)
#     # response = md_query_engine.query(f"Risk Factor of meta in Quarter 2?")
#     # print(response)

# if __name__ == "__main__":
#     main()


