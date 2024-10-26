import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from holdings import iterate_calendar
from openpyxl import Workbook
from io import BytesIO


# Streamlit app
def main():
    st.title("Holdings and Transactions Viewer")
    st.write("Please upload your **Holdings** and **Transactions** CSV files.")

    # File uploaders for CSV files
    holdings_file = st.file_uploader("Upload Holdings CSV", type=["csv"])
    transactions_file = st.file_uploader("Upload Transactions CSV", type=["csv"])

    # Date input for start and end dates
    start_date = st.text_input("Start Date (YYYY-MM-DD)", value="2023-01-01", help="Please enter date in YYYY-MM-DD format.")
    end_date = st.text_input("End Date (YYYY-MM-DD)", value="2023-12-31", help="Please enter date in YYYY-MM-DD format.")

    # Process data when files are uploaded and dates are provided
    if holdings_file and transactions_file and start_date and end_date:
        try:
            # Read CSV files into pandas DataFrames
            holdings_df = pd.read_csv(holdings_file)
            transactions_df = pd.read_csv(transactions_file)
            
            # Process the data
            df = iterate_calendar(start_date=str(start_date),
                                  end_date=str(end_date),
                                  init_holdings=holdings_df,
                                  transactions=transactions_df)
            
            # Plotting using Plotly
            fig = create_plot(df)
            st.plotly_chart(fig, use_container_width=True)
        
        except Exception as e:
            st.error(f"An error occurred: {e}")

def create_plot(df):
    """
    Create a Matplotlib plot from the DataFrame.
    """
    # Create a Matplotlib figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot the data
    ax.plot(df)
    ax.set_title('Holdings and Transactions Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Value')
    ax.grid(True)
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    
    # Return the figure object
    return fig


def create_excel_file(file_name):
    # Create a new Excel workbook and sheet using openpyxl
    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"  # Default sheet

    # Save the workbook to a BytesIO object (in-memory file)
    file_stream = BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)  # Go back to the beginning of the file
    
    return file_stream

# Streamlit app
st.title("Excel File Generator")

# Step 1: Get the filename from the user
file_name = st.text_input("Enter the name for your Excel file (without extension):")

# Step 2: Generate Excel file when user clicks the button
if file_name:
    # Add a download button to trigger the file download
    excel_file = create_excel_file(file_name)

    # Provide the download button
    st.download_button(
        label="Download Excel File",
        data=excel_file,
        file_name=f"{file_name}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    




'''
if __name__ == "__main__":
    main()
'''
