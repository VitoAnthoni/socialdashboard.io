import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import plotly.express as px


st.set_page_config(layout = 'wide',initial_sidebar_state='expanded')

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
#Data Preparation
#Data Import Steps
content = pd.read_csv('https://raw.githubusercontent.com/VitoAnthoni/DataAnalyst/main/Forage/Content.csv')
react = pd.read_csv('https://raw.githubusercontent.com/VitoAnthoni/DataAnalyst/main/Forage/Reactions.csv')
react_type = pd.read_csv('https://raw.githubusercontent.com/VitoAnthoni/DataAnalyst/main/Forage/ReactionTypes.csv')

#Data Prep
content.drop(['Unnamed: 0','User ID','URL'], axis = 1,inplace = True)
content['Category'] = content['Category'].apply(lambda x: x.replace('"', '') if isinstance(x, str) else x).str.title()
react.drop(react[react['Type'].isna()].index,inplace = True)
react.rename(columns={'Content ID':'ContentID'},inplace = True)
content.rename(columns={'Content ID':'ContentID'},inplace = True)
df = pd.merge(react, react_type, how='left', left_on='Type', right_on='Type')
df = pd.merge(df, content, how='left', left_on='ContentID', right_on='ContentID')
df = df.rename(columns={'Type_x': 'Reaction_Type', 'Type_y': 'Type'})
df = df.assign(PromoPoint=lambda x: x['Sentiment'].map({'negative': -1, 'neutral': 0, 'positive': 1}))
df = df.loc[:, ['ContentID', 'User ID', 'Reaction_Type', 'Datetime', 'Sentiment', 'PromoPoint', 'Score', 'Type','Category']]
df['Datetime'] = pd.to_datetime(df['Datetime'])


#Parameter Control
st.sidebar.header('Parameter Control Panel')
#Date Slider
st.sidebar.subheader('Date Parameter')
st.sidebar.write('Date slider used to filtering out until which is the last date the data needs to be visualized')
start_date = date(2020, 6, 1)
end_date = date(2021, 6, 18)
selected_date_range = st.sidebar.slider('Select a date range', start_date, end_date, (start_date, end_date), timedelta(days=1))

#Categorical Drop downlist
selected_Category = st.sidebar.selectbox('Select a Category', df['Category'].unique())



st.sidebar.markdown('''
-----------------
 [Forage Virtual Internship](https://www.theforage.com/virtual-internships/prototype/hzmoNKtzvAzXsEqx8/data-analytics-virtual-experience?ref=onBPrNbfcG9Ek4MCZ&forceFastTrackV2=true#lp)
-----------------
''')
st.sidebar.markdown('''
-----------------
 [Analysis Jupyter Notebook ](https://github.com/VitoAnthoni/DataAnalyst/blob/main/Forage/Forage%20Data%20Analysis.ipynb)
-----------------
''')
st.sidebar.markdown('''
-----------------
 [About Me ](https://www.linkedin.com/in/vito-anthoni-stanpo-4a5924199/)
-----------------
''')
#HEADER
st.title('Social Media Dashboard Analysis')
st.markdown(
    '''
    The business questions that are created in this problem are:
    1. How does the **activity of the users** on daily basis ?
    2. What does the users **preferred type of contents** ? Does Social Buzz needs to concentrate ?
    3. How does the **sentiments** provided for the social buzz ?
    4. What types of **contents category** should the focused on ?
    ''',
    unsafe_allow_html=True
)

#Row A
# convert selected_date_range to datetime objects
start_datetime = datetime.combine(selected_date_range[0], datetime.min.time())
end_datetime = datetime.combine(selected_date_range[1], datetime.min.time()) + timedelta(days=1)

# filter dataframe based on selected date range
df_filtered = df.loc[(df['Datetime'] >= start_datetime) & (df['Datetime'] <= end_datetime)]

#1st Row Showing The Bars First
st.markdown(
    """
    ## Users Consistentency Daily Activities

    Scrolling  we can see **Consistent unique users** active on Social Buzz
    """
)
# create bar chart of daily unique users
daily_unique_users = df_filtered.groupby(df_filtered['Datetime'].dt.strftime('%Y-%m-%d')).agg({'User ID': pd.Series.nunique}).reset_index()
fig = px.bar(
    daily_unique_users, 
    x='Datetime', 
    y='User ID',
    title = 'Active Users',
    labels={
        "x": "Daily Date",
        "y": "Number of Active Users"
    },
    height=600,
    width=1000)
fig.update_layout(
    xaxis_title="Daily Date",
    yaxis_title="Number of Active Users",
    yaxis=dict(
        tickformat=".0f"  # Format y-axis labels as integers
    )
)
st.plotly_chart(fig)


#Row B
# Compute content counts by year-month and content type
st.markdown(
    """
    ## Contents Compositions Basis

    Scrolling  we can see **Consistent Compositions** across Social Buzz with 1/4 each
    """
)
content_compositions = (
    df_filtered.groupby([df_filtered['Datetime'].dt.strftime('%Y-%m'), "Type"])
    .ContentID.count()
    .unstack()
    .fillna(0)
)
comp_pct = content_compositions.apply(lambda x: x * 100 / x.sum(), axis=1)
fig2 = px.bar(
    comp_pct,
    x=comp_pct.index,
    y=comp_pct.columns,
    barmode="stack",
    title="Contents Compositions in Social Buzz",
    labels={
        "x": "Year-Month",
        "y": "Content Compositions (%)",
        "color": "Content Type"
    },
    range_y=[0, 100],
    height=600,
    width=1000,
    category_orders={"x": sorted(comp_pct.index.unique())},
)
fig2.update_layout(
    xaxis_title="Month",
    yaxis_title="Compositions (%)",
    yaxis=dict(
        tickformat=".0f"  # Format y-axis labels as integers
    )
)
st.plotly_chart(fig2)

#Row C consists of Two main concerns which are Sentiments compositions as well as The Top 5 Category
df_filtered_cat = df.loc[(df['Datetime'] >= start_datetime) & (df['Datetime'] <= end_datetime)]

reaction_composition = (
    df_filtered_cat.groupby(["Category","Sentiment","Reaction_Type"])
    .ContentID.count()
    .unstack()
    .fillna(0)
)

reaction_pct = pd.DataFrame(reaction_composition.loc[selected_Category])*100/pd.DataFrame(reaction_composition.iloc[1:]).sum(axis = 0)

fig3 = px.bar(
    reaction_pct,
    x=reaction_pct.index,
    y=reaction_pct.columns,
    barmode="stack",
    title="Contents Compositions in Social Buzz",
    labels={
        "x": "Sentiment",
        "y": "Reaction Compositions (%)",
        "color": "Reaction_Type"
    },
    range_y=[0, 50],
    height=600,
    width=500,
    category_orders={"x": sorted(comp_pct.index.unique())},
)

fig3.update_layout(
    xaxis_title="Sentiment",
    yaxis_title="Percentage (%)",
    yaxis=dict(
        tickformat=".0f"  # Format y-axis labels as integers
    )
)

st.markdown(
    """
    ## Content Category Ranking

    Ranking score is calculated by **NPV** (Net Promotor Value).It is number of users giving positive sentiments deducted by number of users gives negative response.
    Then by using reaction scoring from social buzz we can use it to make it as **Head to Head** tie breaker. Using this ranked we can find
    what top 5 Content Category on Social Buzz preference.

    Using the visualization we can explore each category and how they feel.
    """
)


rank_cat = df_filtered.groupby('Category').aggregate({'PromoPoint':'sum','Score' : 'mean','ContentID':'count'})

c1, c2 = st.columns((6,4))
with c1:
    st.markdown('### Sentiment Analysis')
    st.plotly_chart(fig3)
with c2:
    st.markdown(" ### Top Ranking Category ")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.dataframe(rank_cat)

st.markdown(
    """
    ### CLOSING
    The business insights we can see that :
    1. There is equally distributed preference on content type and stable daily active users on the platform of 58 Daily Users
    2. The top 5 trendy categories are Science, Healthy Eating, Technology , Animal and Culture
    '''
    """
)