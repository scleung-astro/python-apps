# this is a short Python Apps using StreamLit as GUI for portfolio
# management. By entering the choices of stocks, the apps will
# calculate the corresponding expected return, volatility
# and the efficient frontier. 
#
# Idea taken from https://towardsdatascience.com/python-markowitz-optimization-b5e1623060f5
#
# Written by Shing Chi Leung at 6 March 2021

from numpy.lib.scimath import sqrt
import pandas as pd
import yfinance as yf
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

# import data from yfinance and calculate the daily return (scaled to annual
# return), and also variances
@st.cache
def load_data(assets, start_date="2016-01-01", end_date="2020-12-31"):

    # list for the historical prices
    df_list = []
    for asset in assets:
        df = yf.download(asset, start=start_date, end=end_date)
        df_list.append(df)
    
    # list for individual stock's averaged return and variance
    avg_rtns = []
    avg_vols = []

    for df in df_list:

        # artithematic way
        #df["Diff"] = df["Adj Close"].diff() / df["Adj Close"].shift(1) * 100

        # logarithmic way
        df["Diff"] = np.log(df["Adj Close"] / df["Adj Close"].shift(1)) 

        # add to the lists for output
        avg_rtns.append(df["Diff"].mean() * 252)
        avg_vols.append(df["Diff"].var() * 252)

        # compute the scaled price for culmulative return
        price_reference = df.iloc[0]["Adj Close"]
        df["Scaled"] = df["Adj Close"] / price_reference

    return df_list, avg_rtns, avg_vols

# this method calls the pandas to read the wikipedia page for the S&P component stocks
@st.cache
def load_sp500_components():
    df = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    return df.drop("SEC filings", axis=1).set_index("Symbol")

# obsolete
# method to return the company symbol from its company name
def get_stock_label(components, company):
    a = components[components["Security"] == company].index
    return a

def main():

    # create the background data 
    components = load_sp500_components()
    stock_list = components.index

    # build the header
    st.header("Portfolio Management Apps")
    st.write("Choose your stocks and their allocation. This apps will calculate the cumulative return of the past 5 years. "
            "It will use your stock list and compute the average return and covariance matrix. "
            "Then the apps will find the particular allocation so that the Sharpe ratio is maximized. ")
    st.write("**Caution**: This is an app aiming at practicing StreamLit GUI programming and the use of Sharpe ratio in financial "
            "analysis. All results here are only for demonstration of my programming skills and have completely no "
            "intention for any form of financial advice. Do not use any part of this program as any form of suggestion or "
            "evidence for your real life investment or speculation.")

    # build the sidebar
    st.sidebar.title("Construct your profile")
    num_stocks = st.sidebar.slider("Number of stocks", value=1, min_value=1, max_value=10, step=1)

    stock_lists = [None for i in range(num_stocks)]
    stock_frac = [0 for i in range(num_stocks)]

    # build the array of stock selections and sliders 
    st.sidebar.subheader("Customize your Stock List")
    total_ratio = 0
    for i in range(num_stocks):
        stock_lists[i] = st.sidebar.selectbox("Stock " + str(i+1), stock_list, index=i)
        stock_frac[i] = st.sidebar.slider("Initial Fraction", value=0.01, min_value=0.01, max_value=1.0-total_ratio, step=0.01)
        total_ratio += stock_frac[i]
    df_list, avg_rnts, avg_vols = load_data(stock_lists)

    # update the data based on selected stocks
    fetch_data = st.sidebar.button("Update Data")
    if fetch_data:
        df_list, avg_rnts, avg_vols = load_data(stock_lists)

    # display prices of selected stock
    show_current_portfolio = st.sidebar.checkbox("Displace price chart", value=False)
    if show_current_portfolio:
        portfolio_frame = st.empty()

        # build the figure by plotting all the historical price
        fig, ax = plt.subplots()
        for i, df in enumerate(df_list):
            ax.plot(df["Scaled"], label=stock_lists[i])
        ax.legend()
        ax.set_xlabel("Year")
        ax.set_ylabel("Price relative to 2016")

        # post the figure on the screen
        portfolio_frame.pyplot(fig)

    # option: performance of your portfolio
    display_current_portfolio = st.sidebar.checkbox("Display current portfolio")
    if display_current_portfolio:

        st.header("Performance Analysis")

        # build the figure 
        portfolio_frames = st.beta_columns(2)
        fig2, ax2 = plt.subplots()
        ax2.pie(stock_frac, labels=stock_lists, autopct='%1.1f%%')
        ax2.set_title("Asset Allocation")

        # post the figure on the screen
        portfolio_frames[0].pyplot(fig2)

        # convert to dataframe for pretty output
        df_summary = pd.DataFrame(data={"Avg return":avg_rnts, "Avg volatility":avg_vols}, index=stock_lists)
        portfolio_frames[1].write(df_summary)

        # compute the cumulative return
        dates = df_list[0].index
        cost = np.zeros(len(dates))
        for i, df in enumerate(df_list):
            cost += stock_frac[i] * df["Scaled"].to_numpy() 

        revenue_frame = st.empty()

        # plot the cumulative return
        fig3, ax3 = plt.subplots()
        ax3.plot(dates, cost)
        ax3.set_title("Cumulative Return since 2016 of your portfolio")
        ax3.set_xlabel("Year")
        ax3.set_ylabel("Cumulative Return")

        #post the figure on the screen
        revenue_frame.pyplot(fig3)

    # option: calculate covariance and then Sharpe ratio
    display_covariance = st.sidebar.checkbox("Display covariance")
    if display_covariance:

        # build the covariance matrix
        covars = [[1 for i in range(num_stocks)] for j in range(num_stocks)]
        for i in range(num_stocks):
            for j in range(num_stocks):
                series1 = df_list[i]["Diff"].fillna(0).to_numpy()
                series2 = df_list[j]["Diff"].fillna(0).to_numpy()
                series_bind = np.hstack((series1, series2))
                covar = np.cov(series_bind)
                covars[i][j] = float(covar * 252)
                covars[j][i] = float(covar * 252)
                #print(type(covar), covar.shape)
        covars = np.array(covars)

        # convert to dataframe for pretty output
        st.header("Covariance of your selected stocks")

        df_covars = pd.DataFrame(covars, columns=stock_lists, index=stock_lists)
        covariance_frames = st.beta_columns(2)
        covariance_frames[0].write(df_covars)

        # compute the user portfolio return and volatility
        avg_rnt = np.sum(np.array(avg_rnts) * np.array(stock_frac))
        avg_vol =  np.sqrt(np.dot(np.array(stock_frac), np.dot(covars, np.array(stock_frac))))
        
        # output for reference
        covariance_frames[1].write("Your average daily return is {:.2}".format(avg_rnt))
        covariance_frames[1].write("Your portfolio volatility is {:.2}".format(avg_vol))

        st.header("Efficient Frontier")

        # compute the efficient frontier by Monte-Carlo
        all_weights = np.zeros((5000, num_stocks))
        ret_arr = np.zeros(5000)
        vol_arr = np.zeros(5000)
        sharpe_arr = np.zeros(5000)

        for i in range(5000):
            weights = np.array(np.random.random(num_stocks))
            weights = weights/np.sum(weights)

            all_weights[i,:] = weights
            ret_arr[i] = np.sum(np.array(avg_rnts) * weights)
            vol_arr[i] = np.sqrt(np.dot(weights.T, np.dot(covars, weights)))
            sharpe_arr[i] = ret_arr[i] / vol_arr[i]

        # get the best profile
        sharpe_max_idx = sharpe_arr.argmax()
        max_ret = ret_arr[sharpe_max_idx]
        max_vol = vol_arr[sharpe_max_idx]

        # plot the efficient frontier
        frontier_frame = st.empty()
        fig4, ax4 = plt.subplots()
        ax4.scatter(vol_arr, ret_arr, c=sharpe_arr, cmap="winter")
        ax4.scatter(max_vol, max_ret, c="red", label="best model")
        ax4.scatter(avg_vol, avg_rnt, c="black", label="your portfolio")
        ax4.set_label("Efficient Frontier Plot")
        ax4.set_xlabel("Annual volatility")
        ax4.set_ylabel("Annual return")
        ax4.legend()

        # post the figure on the screen 
        frontier_frame.pyplot(fig4)

        st.subheader("Best Model Weights:")
        for i in range(num_stocks):
            st.write("{}: {:.2}".format(stock_lists[i], all_weights[sharpe_max_idx,i]))

    st.sidebar.title("About")
    st.sidebar.info("A short app for building and testing your investment portfolio. "
                    "For practicing StreamLit GUI and theoretical financial analysis. "
                    "The apps will compute the corresponding returns and volatility, "
                    "and derive the best model based on Sharpe ratio analysis. "
                    "Written by Shing Chi Leung at 6 March 2021.")

    #print(df_list[0]["Diff"].head(5))

if __name__ == "__main__":
    main()