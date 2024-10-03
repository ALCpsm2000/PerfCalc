''' The purpose of this Module is to create an modele an object that has the holdings of a portfolio as well as other important transaction information'''

from datetime import datetime, timedelta
import pandas as pd
from pricing import pricing_df
import numpy as np 
import matplotlib.pyplot as plt


df = pd.read_csv("holdings.csv")
df2 = pd.read_csv("transactions.csv")

valuations = {} # k datetime and v port valuation 

def iterate_calendar(start_date:str, 
                     end_date:str, 
                     init_holdings:pd.DataFrame, 
                     transactions:pd.DataFrame):
    
    ''' Dates are expected to be passed as YYYY-MM-DD '''
    
    #converts the dates in the transaction file from str to datetime
    transactions["Date"] = pd.to_datetime(transactions["Date"])
    transactions["Date"] = transactions["Date"].dt.strftime('%Y-%m-%d %H:%M:%S')  
    
    trans = False
    global creator
    creator = {} #this dictionary will hold all our instances of date Holdings with the datetime as key and the holding object as value
    global valuations
    valuations = {} # k datetime and v port valuation   

    transactions = transactions.sort_values(by='Date', ascending=True) #should already be in order but just in case

    stored_valuation = pricing_df(startdate= start_date,
                                  enddate= end_date,
                                  holdings_df = init_holdings,
                                  transactions_df= transactions)
    print(stored_valuation)

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        current_date = start
    except:
        exit

    while current_date <= end:
        #checks if there was a transaction on that date
        
        if str(current_date) in transactions["Date"].values:
            print("transbeingsettotrue")
            trans = True       
        #to be executed only for the first instance
        if current_date == start:
            creator[current_date] = Holdings(holdings = init_holdings,
                                             date = current_date,
                                             transaction = trans,
                                             pricing_df= stored_valuation)
            creator[current_date].priceit()
            valuations[str(current_date)] = creator[current_date].valuation 
            
            _prev_holdings = creator[current_date].holdings  #initialisation of _prev holdings var

        #to be executed for every other instance that is not the first. No need to overwrite _prev_holdings var.
        if current_date != start:
            creator[current_date] = Holdings(holdings = _prev_holdings,
                                             date = current_date,
                                             transaction = trans,
                                             pricing_df= stored_valuation)
            creator[current_date].priceit()
            valuations[str(current_date)] = creator[current_date].valuation 

        if trans:
            #adjust the holdings the day there is a transaction and overwrites the data to be used for the next day
            
            creator[current_date].transaction_df = transactions[transactions["Date"] == str(current_date)] #passing the transactions for that date
            creator[current_date].adjustments() #adjusting the holdings
            creator[current_date].priceit() #repricing    
            valuations[str(current_date)] = creator[current_date].valuation #writing our valuation to our dictionary
            #once the instance.holdings have been modified they will be the holdings of the next instance
            _prev_holdings = creator[current_date].holdings
            trans = False 
           
        #to be executed always    
        current_date = current_date + timedelta(days = 1)
    
    df = pd.DataFrame.from_dict(valuations, orient="index")
    return df.dropna()


class Holdings():

    
    '''This class modules the instance of a holding in any given date'''
    
    def __init__(self, holdings:pd.DataFrame, 
                 date:datetime, 
                 transaction:bool,
                 pricing_df = pd.DataFrame(), 
                 transactions_df = pd.DataFrame()):
        
        self.holdings = holdings
        self.date = date
        self.transaction = transaction
        self.transaction_df = transactions_df
        self.pricing_df = pricing_df


    def adjustments(self):
        ''' Adjustment made to holdings incase of transactions'''

        working_df_trans = self.transaction_df
        working_df_holdings = self.holdings
     
        working_df_trans["total"] = working_df_trans["Quantity"] * working_df_trans["Price"]  
        delta_cash = working_df_trans["total"].sum()

    
        for row in working_df_trans.itertuples():
    # Check if the Ticker exists in the holdings DataFrame
            if row.Ticker in working_df_holdings['Ticker'].values:
                # If it exists, update the quantity
                working_df_holdings.loc[working_df_holdings["Ticker"] == row.Ticker, "Quantity"] += row.Quantity
            else:
                # If it doesn't exist, add a new row with the Ticker and Quantity
                new_row = {'Ticker': row.Ticker, 'Quantity': row.Quantity}
                working_df_holdings = working_df_holdings.append(new_row, ignore_index=True)

        
        #overwritting adjusting cash position  and holdings again
        working_df_holdings.loc[working_df_holdings["Ticker"] == "EUR", "Quantity"] = float(working_df_holdings.loc[working_df_holdings["Ticker"] == "EUR", "Quantity"]) + float(delta_cash) #currently EUR cash is hardcoded in
        self.holdings = working_df_holdings
        print(self.holdings)
    
    def priceit(self):
        
        '''This function will take a Dataframe with pricing and merge it to the holdings data frame. The adjustments df has to be ran before hand or else there could be holdings that do not get priced '''
        _false_valuation = False
        working_price_df = self.pricing_df
        working_holdings_df = self.holdings
        print(self.date)
        
        for row in working_holdings_df.itertuples():
            if row.Ticker != "EUR": #we will never get a price for cash component
                try:
                    # Attempt to update the 'Price' column
                    working_holdings_df.loc[working_holdings_df["Ticker"] == row.Ticker, "Price"] = working_price_df.loc[str(self.date), row.Ticker]
                except KeyError:
                    # Handle the case where the ticker or index is not found
                    print(f"Ticker {row.Ticker} not found in working_price_df or issue in updating.")
                    _false_valuation = True
                    self.valuation = np.nan
                    try:
                        working_holdings_df.loc[working_holdings_df["Ticker"] == row.Ticker, "Price"] = np.nan 
                    except:
                        print("Could not overwrite df")
                        continue
                    continue  # Continue to the next iteration
        working_holdings_df.loc[working_holdings_df["Ticker"] == "EUR", "Price"] = 1
        working_holdings_df["Total"] = working_holdings_df["Quantity"] * working_holdings_df["Price"]
        if _false_valuation:
            self.valuation = np.nan

        else:

            try:
                self.valuation = working_holdings_df["Total"].sum()
            except:
                self.valuation = np.nan 
        print(self.valuation)
        self.holdings = working_holdings_df



df = iterate_calendar("2023-01-01", "2023-01-31", df, df2)
df = df.dropna()
df.plot()
plt.show()

