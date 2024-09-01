import yfinance as yf 
import pandas as pd 
from datetime import datetime, timedelta


df = pd.read_csv("holdings.csv")
df2 = pd.read_csv("transactions.csv")


def pricing_df(startdate:str,
               enddate:str,
               holdings_df:pd.DataFrame,
               transactions_df:pd.DataFrame):
    
    tickers_to_query = pd.concat([holdings_df["Ticker"], transactions_df["Ticker"]]).drop_duplicates() #incase we buy stocks that are not in our initial holdings we must concat and drop duplicates
    tickers_to_query = tickers_to_query[tickers_to_query != "EUR"] #drops the CASH component
    tickers_to_query = tickers_to_query.astype(str).str.cat(sep=" ") #makes it useable my yahoo finance
    df = yf.download(tickers = "MAP.MC ITX.MC",
                 start = mod_day(startdate,-1),
                 end = mod_day(enddate,1),
                 progress = False)
    df = df["Adj Close"]
    df.index = df.index.strftime('%Y-%m-%d %H:%M:%S')

    return df

def mod_day(date_str, dif):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")

    # Subtract one day using timedelta
    new_date_obj = date_obj + timedelta(days=dif)
    new_date_str = new_date_obj.strftime("%Y-%m-%d")

    return(str(new_date_str))


