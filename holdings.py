''' The purpose of this Module is to create an modele an object that has the holdings of a portfolio as well as other important transaction information'''

from datetime import datetime, timedelta
import pandas as pd


df = pd.read_csv("holdings.csv")
df2 = pd.read_csv("transactions.csv")


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

    transactions = transactions.sort_values(by='Date', ascending=True) #should already be in order but just in case

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
                                             transaction = trans)
            
            _prev_holdings = creator[current_date].holdings 

        #to be executed for every other instance that is not the first. No need to overwrite _prev_holdings var.
        if current_date != start:
            creator[current_date] = Holdings(holdings = _prev_holdings,
                                             date = current_date,
                                             transaction = trans)

        if trans:
            #adjust the holdings the day there is a transaction and overwrites the data to be used for the next day
            
            creator[current_date].transaction_df = transactions[transactions["Date"] == str(current_date)] #passing the transactions for that date
            
            creator[current_date].adjustments()
            
            
            
            
            
            #once the instance.holdings have been modified they will be the holdings of the next instance
            _prev_holdings = creator[current_date].holdings
            trans = False
           
        #to be executed always    
        current_date = current_date + timedelta(days = 1)


class Holdings():
    '''This class modules the instance of a holding in any given date'''
    def __init__(self, holdings:pd.DataFrame, 
                 date:datetime, 
                 transaction:bool, 
                 transactions_df = pd.DataFrame()):
        
        self.holdings = holdings
        self.date = date
        self.transaction = transaction
        self.transaction_df = transactions_df

    def adjustments(self):
        ''' Adjustment made to holdings incase of transactions'''

        working_df_trans = self.transaction_df
        working_df_holdings = self.holdings
     
        working_df_trans["total"] = working_df_trans["Quantity"] * working_df_trans["Price"]  
        delta_cash = working_df_trans["total"].sum()

        for row in working_df_trans.itertuples():
            # merges new holdings into transactions
            working_df_holdings.loc[working_df_holdings["Ticker"] == row.Ticker, "Quantity"] = working_df_holdings.loc[working_df_holdings["Ticker"] == row.Ticker, "Quantity"] + row.Quantity
            print(working_df_holdings)
        
        #overwritting adjusting cash position  and holdings again
        working_df_holdings.loc[working_df_holdings["Ticker"] == "EUR", "Quantity"] = float(working_df_holdings.loc[working_df_holdings["Ticker"] == "EUR", "Quantity"]) + float(delta_cash) #currently cash is hardcoded in
        self.holdings = working_df_holdings
        print(self.holdings)




iterate_calendar("2023-01-01", "2023-12-31",df, df2)
