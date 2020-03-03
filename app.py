# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 05:48:29 2020
@author: glawson
"""


"""
*******************************************************************************
To view the dashboard:
    1) Save the script in a location that you can easily navigate to using the Python 
        terminal.  I used my C: Drive because I couldn't figure out how to get
        to my Google drive.
    2) In your Python terminal, use cd to get to the appropriate directory
    3) Input "python app.py" once you are in the correct directory where the file
        lives.
    4) Visit http://127.0.0.1:8050/ in your web browser

Examples:
    Towards Data Science example    
        https://towardsdatascience.com/value-investing-dashboard-with-python-beautiful-soup-and-dash-python-43002f6a97ca
    Julia Rodd's MSDS 498 Project
        https://github.com/dashpound/review_dashboard
*******************************************************************************
"""

# =============================================================================
# Import Packages
# =============================================================================

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output
import base64
import numpy as np
import pandas as pd
from yahoo_historical import Fetcher

from dateutil.relativedelta import relativedelta                                                                                                                  
from datetime import date 


# =============================================================================
# Set Date Parameters
# =============================================================================

# Paremeters used in pulling tweet data.
#half = relativedelta(months=6) #Currently set at 6 months ago to current day
half = relativedelta(months=9) #Currently set at 9 months ago to current day to align with Phase I deliverable
today = pd.Timestamp.today()
six_mo_ago = today - half

# Parameters used in pulling stock price data.
five_yrs = relativedelta(months=60) #Currently set at 5 yrs ago to current day
today = date.today()#
five_yrs_ago = today - five_yrs
five_yrs_ago=five_yrs_ago.strftime('%Y-%m-%d')
# Convert dates to yr, month, and day for FB Prophet input
yr=int(five_yrs_ago[0:4])
mo=int(five_yrs_ago[5:7])
dy=int(five_yrs_ago[8:10])


# =============================================================================
# Import Data
# =============================================================================

#****** All data imports should be considered to use live pipeline in future *******

# Import predictions.  
preds = pd.read_csv('https://raw.githubusercontent.com/msds498-voracious/Dashboard/master/predictions.csv')
# Import tweets.
all_tweets = pd.read_csv('https://raw.githubusercontent.com/msds498-voracious/Dashboard/master/tweets_since_2017.csv')
# Import top handles.
top_handles = pd.read_csv('https://raw.githubusercontent.com/msds498-voracious/Dashboard/master/top_names_df.csv')

###############################################################################
# Prepare tweet data for use in dashboard.

# Convert dates to datetime
all_tweets['date'] = pd.to_datetime(all_tweets['date'])

# Mask data to only use specified time period of tweets
mask = (all_tweets.date >= six_mo_ago) & (all_tweets.date <= today)
all_tweets = all_tweets.loc[mask]

# Drop duplicate tweets
all_tweets.drop_duplicates(subset=['date', 'screen_name', 'tweet_text'],
                           keep = False, inplace = True) 
all_tweets = all_tweets.reset_index(drop=True)

# Create new dataframe to convert stock mentions to one column for one-hot-encoding
# where to link each tweet to the mentioned stocks
tweets_comb_stock = pd.DataFrame(columns=('Date', 'Screen Name', 'Sentiment',
                                          'No. of Likes', 'No. of Replies', 'No of Retweets', 'Tweet Text', 'fb',
                                          'aapl', 'amzn', 'nflx', 'googl',
                                          'faang', 'non-faang','Num_Tweets','Tweet_Days', 'Accuracy_30d'))
tweets_comb_stock[['Date','Screen Name','Sentiment', 'No. of Likes', 'No. of Replies', 'No of Retweets', 'Tweet Text']]=all_tweets[['date','screen_name','polarity1', 'likes', 'replies', 'retweets','tweet_text']]
tweets_comb_stock['fb']=all_tweets['fb']+all_tweets['facebook']
tweets_comb_stock['aapl']=all_tweets['aapl']+all_tweets['apple']
tweets_comb_stock['amzn']=all_tweets['amzn']+all_tweets['amazon']
tweets_comb_stock['nflx']=all_tweets['nflx']+all_tweets['netflix']
tweets_comb_stock['googl']=all_tweets['googl']+all_tweets['google']
tweets_comb_stock['faang']=all_tweets['fang']+all_tweets['faang']

#New dataframe that holds only FAANG tweets
faang_tweets = tweets_comb_stock.sort_values(by=['Date'])
faang_tweets_df = faang_tweets[['Date', 'Screen Name', 'Sentiment',
                                          'No. of Likes', 'No. of Replies', 'No of Retweets', 'Tweet Text']]


# =============================================================================
# Create App
# =============================================================================

# Import Dash stylesheet
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Create the app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# Set dashboard text colors
colors = {
    'text': '#4AA02C'
}

# Add logo image to page
image_filename = 'voracious2.png' # Must live in GitHub repository
encoded_image = base64.b64encode(open(image_filename, 'rb').read()).decode('ascii')


# =============================================================================
# Create the Layout
# =============================================================================

app.layout = html.Div( children = [ 
    
    #Logo
    html.Div( children=[
        html.Img(src='data:image/png;base64,{}'.format(encoded_image))
        ], style={'width': '15%',
                    'float': 'left',
                    'display': 'inline-block',
                    'verticalAlign': 'top'
                    }),
    
    #Title Block Header    
    html.Div( children=[
        html.H1('The Future of Stock Market Investing'),
        ], style={'width': '100%',
                    'display': 'inline-block',
                    'textAlign': 'bottom',
                    'color':colors['text']
                    }),
    
    #Dropdown and prediction table
    html.Div( children=[
        # First let users choose stocks
        html.H2('Choose a stock ticker'),
        dcc.Dropdown(
            id='my-dropdown',
            options=[{'label': 'Apple', 'value': 'AAPL'},
                     {'label': 'Amazon', 'value': 'AMZN'},
                     {'label': 'Facebook', 'value': 'FB'},
                     {'label': 'Google', 'value': 'GOOGL'},
                     {'label': 'Netflix', 'value': 'NFLX'}
                     ],
            value='AAPL'),
        #html.H2('Future Price Movement Predictions'),
        html.H2(id='future-prediction-title'),
        html.Table(id='prediction-table'),
        html.P(''),
        ], style={'width': '20%',
                    'display': 'inline-block',
                    'align': 'center'#,
                    }),

    #Graph the stock price in the top right corner
    html.Div( children = [
        #html.H2('5 years stocks price graph'),
        html.H2(id='stock-graph-title'),
        dcc.Graph(
                figure={'layout':{
                            'title':'Stock Price over Time',
                            'xaxis':{
                                'title':'Time'
                                },
                            'yaxis':{
                                'title':'Daily Close Price (USD)'
                                }
                        }}, id='my-graph'),
        html.P('')
        ], style={'width': '75%',
                    'float': 'right',
                    'display': 'inline-block'
                    }),

    
    #Graph the stock price in the top right corner
    html.Div( children = [
        #html.H2('5 years stocks price graph'),
        html.H2(id='recent-news-title')
        ], style={'width': '100%',
                    #'float': 'right',
                    'display': 'inline-block'
                    }),
    #Tweet table
    dash_table.DataTable(
        id='stock-tweets-table',
        style_data={
        'whiteSpace': 'normal',
        'height': 'auto'
    },
        columns=[
            {"name": i, "id": i, } for i in faang_tweets_df.columns
        ],
#        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
#        column_selectable="single",
#        row_selectable="multi",
#        row_deletable=True,
#        selected_columns=[],
#        selected_rows=[],
        page_action="native",
#        page_current= 0,
        page_size= 10,
        style_cell={'textAlign': 'left','fontSize':15, 'font-family':'sans-serif', 'minWidth': '0px', 'maxWidth': '1000px',
        'whiteSpace': 'normal'},
        style_cell_conditional=[
        {
            'if': {'column_id': 'Region'},
            'textAlign': 'left'
        }]),
            
    #Disclaimer text   
    html.Div( children = [
    dcc.Markdown('''
                 
                 ##### Disclaimer
                 All information and opinions indicated are currently only as of the date of this communication, and are subject to change without notice.  This material is for your private information, and Voracious is not soliciting any action based upon it.  The material is based upon information that we consider reliable, but we do not represent that it is accurate or complete, and it should not be relied upon as such.
                 (a) Voracious is not recommending an action to you;
                 (b) Voracious is not acting as an advisor to you and does not owe a fiduciary duty pursuant to Section 15B of the Exchange Act to you with respect to the information and material contained in this communication;
                 (c) Voracious is acting for its own interests; [and]
                 (d) you should discuss any information and material contained in this communication with any and all internal or external advisors and experts that you deem appropriate before acting on this information or material.
        ''') 
    ], style={'width': '100%',
                    #'float': 'right',
                    'display': 'inline-block'
                    }),
     ]
)
      

# =============================================================================
# Define the Callbacks
# =============================================================================
    
#Stock Graph Title
@app.callback(
    Output('stock-graph-title', 'children'),
    [Input('my-dropdown', 'value')]
)
def update_graph_title(x):
    return "5-Year Stock Data Graph for {}".format(x)

#Recent News Title
@app.callback(
    Output('future-prediction-title', 'children'),
    [Input('my-dropdown', 'value')]
)
def update_fut_pred_title(x):
    return "Future {} Price Movement Predictions".format(x)

#Recent News Title
@app.callback(
    Output('recent-news-title', 'children'),
    [Input('my-dropdown', 'value')]
)
def update_recent_news_title(x):
    return "Recent {} News".format(x)


#Callback for the stocks graph
@app.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value')])
def update_graph(selected_dropdown_value):
    global stockpricedf # Needed to modify global copy of stockpricedf
    ticker_fb = Fetcher(selected_dropdown_value, [yr,mo,dy])
    #ticker_fb = Fetcher('fb', [yr,mo,dy])
    stockpricedf=ticker_fb.get_historical()
    stockpricedf['Date'] = pd.to_datetime(stockpricedf['Date'])
    stockpricedf['Close'] = stockpricedf['Close']
    return {
        'data': [{
            'x': stockpricedf.Date,
            'y': stockpricedf.Close,
            'line':{'color':'green'}
        }]
    }
#Resource to potentially add in a second axis for tweet volume
#https://community.plot.ly/t/multiple-y-axes-name-on-top-of-each-other/10663

# Callback for the prediction table
@app.callback(Output('prediction-table', 'children'), [Input('my-dropdown', 'value')])
def generate_pred_table(selected_dropdown_value,max_rows=10):
    global preddf # Needed to modify global copy of financialreportingdf
    preddf = preds[preds['Ticker']==selected_dropdown_value.lower()]
    preddf = preddf[['1-Day Return','10-Day Return','30-Day Return',]]
      
    # Header
    return html.Table([html.Tr([html.Th(col) for col in preddf.columns])] + [html.Tr([
        html.Td(preddf.iloc[i][col]) for col in preddf.columns
    ]) for i in range(min(len(preddf), max_rows))])
            
# Callback for the tweet table
@app.callback(Output('stock-tweets-table', 'data'), [Input('my-dropdown', 'value')])
def generate_table1(selected_dropdown_value,max_rows=10):
    top_handle_df = top_handles[top_handles['Stock_Names']==selected_dropdown_value.lower()]
    top_handle_df['Screen_Name'].replace('@','',regex=True,inplace=True)
    top_handle_list = top_handle_df['Screen_Name'].tolist()
    top_faang_tweets = faang_tweets[faang_tweets['Screen Name'].isin(top_handle_list)]
    
    top_faang_tweets = top_faang_tweets[top_faang_tweets[selected_dropdown_value.lower()]==1]
    top_faang_tweets = top_faang_tweets.sort_values(by='Date', ascending=False)
    top_faang_tweets['Sentiment'] = np.round(top_faang_tweets['Sentiment'],2)
    top_faang_tweets['Date'] = top_faang_tweets['Date'].dt.strftime('%Y/%m/%d')
    
    return top_faang_tweets[['Date','Screen Name','Sentiment','No. of Likes', 'No. of Replies', 'No of Retweets', 'Tweet Text']].to_dict('records')


# =============================================================================
# Run the App
# =============================================================================
            
if __name__ == '__main__':
    app.run_server(debug=True)
    

