    def _fetch_holdings(self):
        ''' This funcition will fetch the previous days holdings or if init day fetch init holdings'''

        if self.is_start_day:
            self.prev_day_holdings = self.init_holdings
        else:
            self.prev_day_holdings = self.parent_instance_TS.IndividualDays_instances[self.prev_day_str].portfolio_instances[self.name].adjusted_holdings
            self.yesterdays_units = self.parent_instance_TS.IndividualDays_instances[self.prev_day_str].portfolio_instances[self.name].shares
            self.yesterdays_nav = self.parent_instance_TS.IndividualDays_instances[self.prev_day_str].portfolio_instances[self.name].nav
            _day_to_query = self.prev_day_dt
            if self.is_SAA:
                try:
                    while np.isnan(self.yesterdays_nav): 
                        '''incase there isnt a nav yesterday we need to find the latest nav'''
                        print("STARTING WHILE LOOP")
                        _day_to_query = _day_to_query - timedelta(1)
                        _day_to_query_str = datetime.strftime(_day_to_query, '%Y-%m-%d')
                        print(f"querying: {_day_to_query_str}")                
                        returned_nav = self.parent_instance_TS.IndividualDays_instances[_day_to_query_str].portfolio_instances[self.name].nav                        
                        print(f"retruned nav: {returned_nav}")
                        self.yesterdays_nav = returned_nav
                except Exception as e:
                    print(e)
                    exit
               



            self.shares = self.yesterdays_units
            


    def _adjustholdings(self):
        if self.is_trans_day:
                ''' Adjustment made to holdings incase of transactions'''

                working_df_trans = self.transactions.copy()
                working_df_holdings = self.prev_day_holdings
                working_df_trans["total"] = working_df_trans["Quantity"] * working_df_trans["Price"]  #takes care of affect on cash

                
                filtered = working_df_trans[(working_df_trans['Date'] == self.val_day_str) & (working_df_trans['Ticker'] != 'EUR')]
                # Return the sum of the 'total' column or 0 if no relevant rows are found
                delta = filtered['total'].sum() if not filtered.empty else 0


            
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
                working_df_holdings.loc[working_df_holdings["Ticker"] == "EUR", "Quantity"] = float(working_df_holdings.loc[working_df_holdings["Ticker"] == "EUR", "Quantity"]) + float(-delta) #currently EUR cash is hardcoded in
                
                return working_df_holdings

        else:
            #when no need to adjust cuz no transactions
            self.adjusted_holdings = self.prev_day_holdings
        
    def _pricing_df(self):
        '''Creates a df that gets priced and sectors'''
        tickers_to_query = pd.concat([self.adjusted_holdings["Ticker"], self.transactions["Ticker"]]).drop_duplicates() #incase we buy stocks that are not in our initial holdings we must concat and drop duplicates
        tickers_to_query_series = tickers_to_query[tickers_to_query != "EUR"].copy() #drops the CASH component
        tickers_to_query = tickers_to_query_series.astype(str).str.cat(sep=" ") #makes it useable my yahoo finance
        df = yf.download(tickers = tickers_to_query,
                    start = self.val_day_str,
                    progress = False)
        df = df["Adj Close"]
        df.index = df.index.strftime('%Y-%m-%d')
        #query industry data
        industries = dict()
        for ticker in tickers_to_query_series.tolist():
            ticker_object = yf.Ticker(ticker)
            ind_sector = ticker_object.info.get("sector", "other")
            industries[ticker] = ind_sector

        # Create a DataFrame where each row is a ticker and sector
        sector_df = pd.DataFrame(list(industries.items()), columns=["Ticker", "Sector"])
    
        return sector_df, df
            
    def priceit(self):
        
        '''This function will take a Dataframe with pricing and merge it to the holdings data frame. It will also calculate the valuation and do any share adjustment as well as strike NAV's.
        The adjustments df has to be ran before hand or else there could be holdings that do not get priced '''
        _false_valuation = False
        working_sector_df, working_price_df = self._pricing_df()
        working_holdings_df = self._adjustholdings()
        
        for row in working_holdings_df.itertuples():
            if row.Ticker != "EUR": #we will never get a price for cash component
                try:
                    # Attempt to update the 'Price' column
                    working_holdings_df.loc[working_holdings_df["Ticker"] == row.Ticker, "Price"] = working_price_df.loc[self.val_day_str, row.Ticker]
                except KeyError:
                    # Handle the case where the ticker or index is not found
                    _false_valuation = True
                    self.valuation = np.nan
                    try:
                        working_holdings_df.loc[working_holdings_df["Ticker"] == row.Ticker, "Price"] = np.nan 
                    except:
                        continue
                    continue  # Continue to the next iteration
        working_holdings_df.loc[working_holdings_df["Ticker"] == "EUR", "Price"] = 1
        working_holdings_df["Total"] = working_holdings_df["Quantity"] * working_holdings_df["Price"] #ads the total column
        
        if _false_valuation:
            self.valuation = np.nan

        else:

            try:
                _valuation = working_holdings_df["Total"].sum()
                self.valuation = round(_valuation,4)
                working_holdings_df["Weight"] = working_holdings_df["Total"] / self.valuation
            except:
                self.valuation = np.nan 
        merged_df = working_holdings_df.merge(working_sector_df, on="Ticker", how="left") #adding the sectors
        merged_df.loc[merged_df["Ticker"] == "EUR", "Sector"] = "CASH" #manually putting the sector for cash
        self.priced_df = working_holdings_df
        
        #after we value it we must adjust for our 
        
        if self.is_SAA and isinstance(self.valuation, float):
            self.SAA_amount = self.transactions.loc[(self.transactions["Ticker"] == "EUR") & (self.transactions["Date"] == self.val_day_str), "Quantity"].sum()
            print(f"SAA: {self.SAA_amount}")
            print(f"yesterdays nav: {self.yesterdays_nav}")


            num_shares_issue = self.SAA_amount / self.yesterdays_nav
            print(f"Issuing {num_shares_issue}")
            print(f"shares before:{self.shares})")
            self.shares = self.shares + num_shares_issue
            print(f"new num shares: {self.shares}")
            working_holdings_df.loc[self.adjusted_holdings["Ticker"] == "EUR", "Quantity"] = float(working_holdings_df.loc[working_holdings_df["Ticker"] == "EUR", "Quantity"]) + float(self.SAA_amount) #adjust cash for SAA
            #readjusting valuation 
            _valuation = working_holdings_df["Total"].sum()
            self.valuation = round(_valuation,4)
            working_holdings_df["Weight"] = working_holdings_df["Total"] / self.valuation #adjusting the weights
            self.priced_df = working_holdings_df #overwritting the final df
            self.nav = self.valuation / self.shares

        elif isinstance(self.valuation, float):
            self.nav = self.valuation / self.shares

        print(f"The priced DF for {self.val_day_str}: \n {self.priced_df}")
        print(f"The NAV for {self.val_day_str}: \n {self.nav}")
        print(f"The valuation for {self.val_day_str}: \n {self.valuation}")

        print(f"The number of shares is {self.shares}")