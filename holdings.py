''' The purpose of this Module is to create an modele an object that has the holdings of a portfolio as well as other important transaction information'''

from datetime import datetime, timedelta
import pandas as pd


df = pd.read_csv("holdings.csv")
df2 = pd.read_csv("transactions.csv")
#must be put into the function
df2["Date"] = pd.to_datetime(df2["Date"])
df2["Date"] = df2["Date"].dt.strftime('%Y-%m-%d %H:%M:%S')

def iterate_calendar(start_date:str, end_date:str, init_holdings, transactions):
    ''' Dates are expected to be passed as YYYY-MM-DD '''
    trans = False
    global creator
    creator = {}
    transactions = transactions.sort_values(by='Date', ascending=True)

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
            creator[current_date].adjustments()
            _prev_holdings = creator[current_date].holdings
            trans = False
           
        #to be executed always    
        current_date = current_date + timedelta(days = 1)


class Holdings():
    '''This class modules the instance of a holding in any given date'''
    def __init__(self, holdings, date, transaction:bool):
        self.holdings = holdings
        self.date = date
        self.transaction = transaction


    def adjustments(self):
        ''' Adjust incase of transactions'''
        #must overwrite self.holdings
        print("adjustments are being done")


iterate_calendar("2023-01-01", "2023-12-31",df, df2)
