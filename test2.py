    
    def _generate_holdings(self):
        ''' This functions purpose is to generate two dataframes. The first one will create the holdings of the previous day (or initial holdings) 
            this data frame will then be adjusted in the case of TAA or SAA and we will end with the final holdings dataframe '''

        if self.is_start_day:
            ''' in the case of start day the previous day holdings will just be our initial holdings'''
            self.prev_day_holdings_df = self.init_holdings
        else:
            '''in this case we are getting our TS instance and finding the final holdings for yesterday and those will be todays begining holdings'''
            self.prev_day_holdings_df = self.parent_instance_TS.IndividualDays_instances[self.prev_day_str].portfolio_instances[self.name].final_holdings_df
            self.final_holdings_df = self.prev_day_holdings_df #will get overwritten if there is a AA or TAA


        if self.is_SAA or self.is_TAA:
            ''' If there is an asset allocation we must adjust our holdings and CASH to show that'''
            working_prev_day_holdings_df = self.prev_day_holdings_df.copy(deep = True) #our previous day holdings
            working_transactions_df = self.transactions_df_storage[self.name].copy(deep = True) #The transactions for our portfolio
            
            if self.is_SAA:
                ''' Here we must only adjust cash'''
                SAA_amount = working_transactions_df.loc[(working_transactions_df["Ticker"] == "EUR") & (working_transactions_df["Date"] == self.val_day_str), "Quantity"]
                working_prev_day_holdings_df = working_prev_day_holdings_df[working_prev_day_holdings_df["Ticker"] == "EUR"] + SAA_amount
                final_df = working_prev_day_holdings_df #will get overwritten if there is TAA for the TAA adjustments

            if self.is_TAA:
                '''Here we must adjust cash and holdings'''
                TAA_moves_df = working_transactions_df[(working_transactions_df["Date"] == self.val_day_str) & (working_transactions_df["Ticker"] != "EUR")] #wont have the cash line
                TAA_amount = (TAA_moves_df["Quantity"] * TAA_moves_df["Price"]).sum()
                result = pd.merge(working_prev_day_holdings_df, TAA_moves_df, on="Ticker", how="outer", suffixes=("_DF1", "_DF2")) #if SAA then working prev day holdings already has the adjustment
                result.fillna(0, inplace=True)
                result["Quantity"] = result[["quantity_DF1", "quantity_DF2"]].sum(axis=1, skipna=True) #adjust the holdings for transactions
                final_df = result[["Ticker","Quantity"]]
                final_df = final_df.loc[final_df["Ticker"] == "EUR", "Quantity"] + TAA_amount
