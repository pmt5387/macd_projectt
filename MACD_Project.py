from nsepy import get_history
from datetime import date

import requests
import pandas as pd
import numpy as np
from math import floor
from termcolor import colored as cl
import matplotlib.pyplot as plt

plt.rcParams['figure.figsize'] = (20, 10)
plt.style.use('fivethirtyeight')
import warnings
warnings.filterwarnings('ignore')

import streamlit as st

st.title("MACD Buy & Sell Indicator");


st.text("Enter the stock ticker symbol and you will get to know the strategy when to place a trade. I had used 26,12,9 time frame for EMA.");

symbol_input=st.text_input("Enter the stock ticker symbol")

symbol_input


schien_df=get_history(symbol=symbol_input,start=date(2020,1,1),end=date.today());

st.write(schien_df.tail(30))

def get_macd(price, slow, fast, smooth):
    exp1 = price.ewm(span = fast, adjust = False).mean()
    exp2 = price.ewm(span = slow, adjust = False).mean()
    macd = pd.DataFrame(exp1 - exp2).rename(columns = {'Close':'macd'})
    signal = pd.DataFrame(macd.ewm(span = smooth, adjust = False).mean()).rename(columns = {'macd':'signal'})
    hist = pd.DataFrame(macd['macd'] - signal['signal']).rename(columns = {0:'hist'})
    frames =  [macd, signal, hist]
    df = pd.concat(frames, join = 'inner', axis = 1)
    return df

schien_macd= get_macd(schien_df['Close'], 26, 12, 9)

def plot_macd(prices, macd, signal, hist):
    ax1 = plt.subplot2grid((8,1), (0,0), rowspan = 5, colspan = 1)
    ax2 = plt.subplot2grid((8,1), (5,0), rowspan = 3, colspan = 1)

    ax1.plot(prices)
    ax2.plot(macd, color = 'grey', linewidth = 1.5, label = 'MACD')
    ax2.plot(signal, color = 'skyblue', linewidth = 1.5, label = 'SIGNAL')
    try:
        for i in range(len(prices)):
            if str(hist[i])[0] == '-':
                ax2.bar(prices.index[i], hist[i], color = '#ef5350')
            else:
                ax2.bar(prices.index[i], hist[i], color = '#26a69a')
    except Exception as E:
        pass
    plt.legend(loc = 'lower right')

plot_macd(schien_df.Close,schien_macd.macd,schien_macd.signal,schien_macd.hist)

def implement_macd_strategy(prices, data):
    buy_price = []
    sell_price = []
    macd_signal = []
    signal = 0

    for i in range(len(data)):
        if data['macd'][i] > data['signal'][i]:
            if signal != 1:
                buy_price.append(prices[i])
                sell_price.append(np.nan)
                signal = 1
                macd_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                macd_signal.append(0)
        elif data['macd'][i] < data['signal'][i]:
            if signal != -1:
                buy_price.append(np.nan)
                sell_price.append(prices[i])
                signal = -1
                macd_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                macd_signal.append(0)
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
            macd_signal.append(0)
            
    return buy_price, sell_price, macd_signal
            
buy_price, sell_price, macd_signal = implement_macd_strategy(schien_df['Close'], schien_macd)

st.set_option('deprecation.showPyplotGlobalUse', False)

ax1 = plt.subplot2grid((8,1), (0,0), rowspan = 5, colspan = 1)
ax2 = plt.subplot2grid((8,1), (5,0), rowspan = 3, colspan = 1)

ax1.plot(schien_df['Close'], color = 'skyblue', linewidth = 2, label = symbol_input)
ax1.plot(schien_df.index, buy_price, marker = '^', color = 'green', markersize = 10, label = 'BUY SIGNAL', linewidth = 0)
ax1.plot(schien_df.index, sell_price, marker = 'v', color = 'r', markersize = 10, label = 'SELL SIGNAL', linewidth = 0)
ax1.legend()
title_given=symbol_input + " MACD SIGNALS"
ax1.set_title(title_given)
ax2.plot(schien_macd['macd'], color = 'grey', linewidth = 1.5, label = 'MACD')
ax2.plot(schien_macd['signal'], color = 'skyblue', linewidth = 1.5, label = 'SIGNAL')

for i in range(len(schien_macd)):
    if str(schien_macd['hist'][i])[0] == '-':
        ax2.bar(schien_macd.index[i], schien_macd['hist'][i], color = '#ef5350')
    else:
        ax2.bar(schien_macd.index[i], schien_macd['hist'][i], color = '#26a69a')
        
plt.legend(loc = 'lower right')
plt.show()
try:
    st.pyplot()
except Exception as E:
    pass
