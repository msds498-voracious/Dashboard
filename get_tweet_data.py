# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 12:00:53 2020

@author: DELL
"""

import pandas as pd
#import numpy as np
#from datetime import timedelta 
from dateutil.relativedelta import relativedelta                                                                                                                  
#from datetime import date 
#from yahoo_historical import Fetcher

# =============================================================================
# Set Date Parameters
# =============================================================================

half = relativedelta(months=6) 
today = pd.Timestamp.today()
six_mo_ago = today - half

five_yrs = relativedelta(months=60) 
today = pd.Timestamp.today()#
five_yrs_ago = today - five_yrs
five_yrs_ago=five_yrs_ago.strftime('%Y-%m-%d')
yr=int(five_yrs_ago[0:4])
mo=int(five_yrs_ago[5:7])
dy=int(five_yrs_ago[8:10])


stock_names = ['aapl', 'amzn', 'fb', 'googl', 'nflx']
# =============================================================================
# Function to read in tweets and sort according to ticker and date parameters
# =============================================================================

def getrawtweets(ticker):
    
    all_tweets = pd.read_csv('https://raw.githubusercontent.com/msds498-voracious/Dashboard/master/all_tweets3.csv')
    #all_tweets = pd.read_csv('https://raw.githubusercontent.com/msds498-voracious/Finance-NLP/master/faang_tweets.csv')
    top_handles = pd.read_csv('https://raw.githubusercontent.com/msds498-voracious/Dashboard/master/top_names_df.csv')
    top_handle_df = top_handles[top_handles['Stock_Names']==ticker.lower()]
    top_handle_df.rename(columns={'Screen_Name': 'screen_name'}, inplace=True)
    top_handle_list = top_handle_df['screen_name'].tolist()
    all_tweets = all_tweets[all_tweets['screen_name'].isin(top_handle_list)]
    all_tweets['date'] = pd.to_datetime(all_tweets['date'])
    all_tweets = pd.merge(all_tweets,top_handle_df, on='screen_name')
    #all_tweets['date'] = pd.Timestamp(all_tweets['date'])
    
    mask = (all_tweets.date >= six_mo_ago) & (all_tweets.date <= today)
    all_tweets = all_tweets.loc[mask]
    
    all_tweets.drop_duplicates(subset=['date', 'screen_name', 'tweet_text'],
                               keep = False, inplace = True) 
    all_tweets = all_tweets.reset_index(drop=True)
    tweets_comb_stock = pd.DataFrame(columns=('Date', 'Screen Name', 'Sentiment',
                                              'No. of Likes', 'No. of Replies', 'No of Retweets', 'Tweet Text', 'fb',
                                              'aapl', 'amzn', 'nflx', 'googl',
                                              'faang', 'non-faang','Num_Tweets','Tweet_Days', 'Accuracy_30d'))
    tweets_comb_stock[['Date','Screen Name','Sentiment', 'No. of Likes', 'No. of Replies', 'No of Retweets', 'No. of Tweets','No. of Tweet Days','30-Day Return Accuracy','Tweet Text']]=all_tweets[['date','screen_name','polarity', 'likes', 'replies', 'retweets','Num_Tweets','Tweet_Days', 'Accuracy_30d','tweet_text']]
    tweets_comb_stock['fb']=all_tweets['fb']+all_tweets['facebook']
    tweets_comb_stock['aapl']=all_tweets['aapl']+all_tweets['apple']
    tweets_comb_stock['amzn']=all_tweets['amzn']+all_tweets['amazon']
    tweets_comb_stock['nflx']=all_tweets['nflx']+all_tweets['netflix']
    tweets_comb_stock['googl']=all_tweets['googl']+all_tweets['google']
    tweets_comb_stock['faang']=all_tweets['fang']+all_tweets['faang']
    #Create encoding for tweets that don't have a stock reference
    '''for row in range(len(tweets_comb_stock)):
        if tweets_comb_stock.loc[row, ['fb','aapl','amzn','nflx','googl',
                                       'faang']].sum() == 0:
            tweets_comb_stock.loc[row, 'non-faang']=1
        else: 
            tweets_comb_stock.loc[row, 'non-faang']=0
        #print(tweets_comb_stock.loc[row])'''
    
    #New dataframe that holds only FAANG tweets
    #faang_tweets = tweets_comb_stock[tweets_comb_stock['non-faang'] !=1]
    faang_tweets = tweets_comb_stock.sort_values(by=['Date'])
    
    faang_tweets = faang_tweets[faang_tweets[ticker.lower()]==1]
    
    return faang_tweets[['Date','Screen Name','Sentiment','No. of Likes', 'No. of Replies', 'No of Retweets', 'No. of Tweets','No. of Tweet Days','30-Day Return Accuracy','Tweet Text']]

# =============================================================================
# Function to list screen names available for iteration through these names
# =============================================================================
'''
def person_counts(tweet_data):
    counts_by_person_faang = tweet_data.groupby(['Screen Name']).size().sort_values(ascending=False)
    person_faang = counts_by_person_faang.index
    
    return person_faang


# =============================================================================
# Function to list screen names available for iteration through these names
# =============================================================================

def getalltweets():
    
    all_tweets = pd.read_csv('G:/My Drive/MSPA/MSDS 498 - Capstone/Data/Finance-NLP-master/all_tweets3.csv')
    #all_tweets = pd.read_csv('https://raw.githubusercontent.com/msds498-voracious/Finance-NLP/master/faang_tweets.csv')
    all_tweets['date'] = pd.to_datetime(all_tweets['date'])
    #all_tweets['date'] = pd.Timestamp(all_tweets['date'])
    
    mask = (all_tweets.date >= six_mo_ago) & (all_tweets.date <= today)
    all_tweets = all_tweets.loc[mask]
    
    all_tweets.drop_duplicates(subset=['date', 'screen_name', 'tweet_text'],
                               keep = False, inplace = True) 
    all_tweets = all_tweets.reset_index(drop=True)
    tweets_comb_stock = pd.DataFrame(columns=('Date', 'Screen Name', 'Sentiment',
                                              'No. of Likes', 'No. of Replies', 'No of Retweets', 'Tweet Text', 'fb',
                                              'aapl', 'amzn', 'nflx', 'googl',
                                              'faang', 'non-faang'))
    tweets_comb_stock[['Date','Screen Name','Sentiment', 'No. of Likes', 'No. of Replies', 'No of Retweets','Tweet Text']]=all_tweets[['date','screen_name','polarity', 'likes', 'replies', 'retweets','tweet_text']]
    tweets_comb_stock['fb']=all_tweets['fb']+all_tweets['facebook']
    tweets_comb_stock['aapl']=all_tweets['aapl']+all_tweets['apple']
    tweets_comb_stock['amzn']=all_tweets['amzn']+all_tweets['amazon']
    tweets_comb_stock['nflx']=all_tweets['nflx']+all_tweets['netflix']
    tweets_comb_stock['googl']=all_tweets['googl']+all_tweets['google']
    tweets_comb_stock['faang']=all_tweets['fang']+all_tweets['faang']
    #Create encoding for tweets that don't have a stock reference
    for row in range(len(tweets_comb_stock)):
        if tweets_comb_stock.loc[row, ['fb','aapl','amzn','nflx','googl',
                                       'faang']].sum() == 0:
            tweets_comb_stock.loc[row, 'non-faang']=1
        else: 
            tweets_comb_stock.loc[row, 'non-faang']=0
        #print(tweets_comb_stock.loc[row])
    
    #New dataframe that holds only FAANG tweets
    all_faang_tweets = tweets_comb_stock[tweets_comb_stock['non-faang'] !=1]
    all_faang_tweets = tweets_comb_stock.sort_values(by=['Date'])
    
    #faang_tweets = faang_tweets[faang_tweets[ticker.lower()]==1]
    
    return all_faang_tweets[['Date','Screen Name','Sentiment','No. of Likes', 'No. of Replies', 'No of Retweets','Tweet Text']]


# =============================================================================
# Function to sort identify most accurate screen names and sort accordingly
# =============================================================================

polarity_30d = []
delta_p_30d = []
corr_30d = []
pos_neg_30d = []
accuracy_30d = []
stock_tick = []  
scrn_name = []
num_tweets = [] 
tweet_days = [] 
start_date_list = []

def pos_neg_sent_return_name (name, ticker, stock_df, data_tweets):
    #Record Stock Tick and name
    stock_tick.append(ticker)
    scrn_name.append(name)
    print('Name: ', name, ', Ticker: ', ticker)
    
    
    
    data_tweets.index = data_tweets['Date']
    mask = (data_tweets.index > six_mo_ago) & (data_tweets.index <= today)
    data_tweets = data_tweets.loc[mask]
    
    data_tweets = getrawtweets(ticker)
    data_tweets = data_tweets[data_tweets['Screen Name']==name]
    data_tweets['Date'] = pd.to_datetime(data_tweets['Date'])
    data_tweets.index = data_tweets['Date']
    data_tweets_trunc = data_tweets.resample('D').mean()
    print(data_tweets_trunc.head())
    #data_tweets_trunc = data_tweets_trunc[data_tweets_trunc[ticker].notnull()]
    num_tweets.append(len(data_tweets))
    tweet_days.append(len(data_tweets_trunc))
    print('tweet days: ', len(data_tweets_trunc))
    
    #Prep the historic price data
    mask = (stock_df['Date'] > six_mo_ago) & (stock_df['Date'] <= today)
    data_hist = stock_df.loc[mask]
    data_hist.index = data_hist['Date']
    print(data_hist.head())

    #Sentiment polarity to 30-day return
    polarity_30d_list=[]
    delta_p_30d_list=[]
    pos_neg_30d_list=[]
    for day in data_tweets_trunc.index:
        try:
            pol = np.where(data_tweets_trunc.loc[day, ['polarity']].mean()>0,1,0)
            return_end_date = day + timedelta(days=30)
            del_p = np.where(data_hist.truncate(before=return_end_date).iloc[0]['Close'] - 
                             data_hist.truncate(before=day).iloc[0]['Close'] >0,1,0)
            pos_neg = np.where(pol + del_p ==1,0,1)
            polarity_30d_list.append(pol)
            delta_p_30d_list.append(del_p)
            pos_neg_30d_list.append(pos_neg)
        except:
            continue
    corr = np.corrcoef(polarity_30d_list, delta_p_30d_list)[1,0]
    corr_30d.append(corr)
    try:
        accuracy_30d.append(sum(pos_neg_30d_list)/len(pos_neg_30d_list))
    except:
        accuracy_30d.append(np.nan)
        
    #Put correlation
    corr_by_pos_neg_stock_name = pd.DataFrame({'Screen_Name': scrn_name,
                                       'Stock_Names':stock_tick,
                                       'Num_Tweets': num_tweets,
                                       'Tweet_Days': tweet_days,
                                       'Corr_30d':corr_30d,
                                       'Accuracy_30d': accuracy_30d,})
    
    #Set a minimum number of tweet days needed to make it into a top list.  This 
        #prevents handles with two tweets from making list with perfect correlation.
        #Tweet days was used over number of tweets because in several instances
        #handles tweeted several times per day, artificially inflating the correlation.
        
    top_screen_names= corr_by_pos_neg_stock_name[corr_by_pos_neg_stock_name['Tweet_Days']>3]
    
    return top_screen_names
    
# =============================================================================
# Function to pull stock data
# =============================================================================
   
def organize_tweets():
    #data = getrawtweets(ticker)
    #for name in person_counts(data):
    #    pos_neg_sent_return_name (name, ticker, getrawtweets(ticker))
    data_tweets = getalltweets()
    person = person_counts(data_tweets)
    for name in person:
       # data = pd.read_csv('G:/My Drive/MSPA/MSDS 498 - Capstone/Data/Finance-NLP-master/all_tweets3.csv')
        print(name)
        #for stock, df in zip(stock_names, stock_price_df[stock_price_df['Ticker']==stock]):
        for stock in stock_names:
            print(stock)
            df = stock_price_df[stock_price_df['Ticker']==stock]
            pos_neg_sent_return_name (name, stock, df, data_tweets) 
            
organize_tweets()

#Put correlation
corr_by_pos_neg_stock_name = pd.DataFrame({'Screen_Name': scrn_name,
                                   'Stock_Names':stock_tick,
                                   'Num_Tweets': num_tweets,
                                   'Tweet_Days': tweet_days,
                                   'Corr_1d': corr_1d,
                                   'Accuracy_1d': accuracy_1d,
                                   'Corr_10d':corr_10d,
                                   'Accuracy_10d': accuracy_10d,
                                   'Corr_30d':corr_30d,
                                   'Accuracy_30d': accuracy_30d,})

#Set a minimum number of tweet days needed to make it into a top list.  This 
    #prevents handles with two tweets from making list with perfect correlation.
    #Tweet days was used over number of tweets because in several instances
    #handles tweeted several times per day, artificially inflating the correlation.
    
df1 = corr_by_pos_neg_stock_name[corr_by_pos_neg_stock_name['Tweet_Days']>3]
    
#Tabulate highest correlations by person 
print('\nBest Positive/Negative Accuracy for 1-day Return')
print(df1.nlargest(5, ['Accuracy_1d'])) 

print('\nBest Positive/Negative Accuracy for 10-day Return')
print(df1.nlargest(5, ['Accuracy_10d']))

print('\nBest Positive/Negative Accuracy for 30-day Return') 
print(df1.nlargest(5, ['Accuracy_30d']))

#Tabulate highest correlations by person and by stock      
for stock in stock_names:
    df = df1[df1['Stock_Names']==stock]
    print('\n*****************************************************\nStock:  ', stock)
    
    print('\nBest Positive/Negative Accuracy for 1-day Return')
    print(df.nlargest(5, ['Accuracy_1d'])) 
    
    print('\nBest Positive/Negative Accuracy for 10-day Return')
    print(df.nlargest(5, ['Accuracy_10d']))
    
    print('\nBest Positive/Negative Accuracy for 30-day Return') 
    print(df.nlargest(5, ['Accuracy_30d']))

#Select the name of the table that you want to print and set it equal
    #to t below.
t = df1.nsmallest(10, ['Accuracy_30d'])
#print table
print_table(t)

# =============================================================================
# Function to pull stock data
# =============================================================================
#from yahoo_historical import Fetcher

stock_price_list = []

def get_stock_data(ticker):
    ticker_fb = Fetcher(ticker, [yr,mo,dy])
    #ticker_fb = Fetcher('fb', [yr,mo,dy])
    stockpricedf=ticker_fb.get_historical()
    stockpricedf['Date'] = pd.to_datetime(stockpricedf['Date'])
    stockpricedf['Ticker'] = ticker
    
    stock_price_list.append(stockpricedf)

for stock in stock_names:
    get_stock_data(stock)
    
stock_price_df = pd.concat(stock_price_list)
'''