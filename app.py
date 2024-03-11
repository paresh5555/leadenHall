import streamlit as st
import pandas as pd
import numpy as np
import google.generativeai as genai

# Read data
broker_df = pd.read_excel('./data/2024 Dashboard Data.xlsx', sheet_name='Broker stats')
class_df = pd.read_excel('./data/2024 Dashboard Data.xlsx', sheet_name='Class stats')

genai.configure(api_key='AIzaSyCXnLt0axHYvQ9dDLHltCWY1UaOTTxmvPU')
model = genai.GenerativeModel('gemini-pro')


def respond(msg):
    return model.generate_content(
        msg + 'table1' + broker_df.to_csv(index=False) + 'table2' + class_df.to_csv(index=False)).text


# UI customization
st.set_page_config(layout="wide", page_title="LeadenHall Project ", page_icon="🤖")

# Change theme
st.markdown(
    """
    <style>
        body {
            background-color: #f0f2f6;
            color: #333;
        }
        .sidebar .sidebar-content {
            background-color: #334257;
            color: #fff;
        }
        .stButton>button {
            background-color: #1abc9c;
            color: #fff;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar
st.sidebar.title("Chatbot")
st.sidebar.markdown('''Enter your queries here :) ''')
user_input = st.sidebar.text_input("You:", "")

if st.sidebar.button("Send"):
    bot_response = respond(user_input)
    st.sidebar.subheader("Answer")
    st.sidebar.markdown(bot_response)

# Main content
st.title('Brokers, Premiums, and Business Dashboard')
st.subheader('Top 10 Brokers')

# Business logic for filtering and grouping
def filter_and_group(df, year=None, market_type=None):
    filtered_df = df

    if year is not None:
        if year != 'All':
            filtered_df = filtered_df[df['Year'] == year]

    if market_type is not None:
        if market_type != 'Combined':
            filtered_df = filtered_df[df['Market Type'] == market_type]

    grouped_df = filtered_df.groupby('Broker Name').sum().reset_index()
    grouped_df = grouped_df.sort_values(by='GWP', ascending=False)
    grouped_df['Success Rate (%)'] = ((grouped_df['Planned GWP'] - grouped_df['GWP']) / grouped_df['Planned GWP']) * 100
    return grouped_df.head(10)

market_types = list(broker_df['Market Type'].unique()) + ['Combined']
years = list(broker_df['Year'].unique()) + ['All']

# Display filtered data
market_type = st.selectbox('Choose Market Type', market_types)
year = st.selectbox('Choose Year', years)

filtered_data = filter_and_group(broker_df, year, market_type)
st.write(filtered_data[['Broker Name', 'GWP', 'Planned GWP', 'Success Rate (%)']].set_index(filtered_data.columns[0]))
st.bar_chart(data=filtered_data, x='Broker Name', y='GWP')

# Business Case Analysis
st.subheader('Business Case Analysis')

# Business logic for filtering classes
def class_filter(df, class_of_business_filter, class_type_filter):
    filtered_df = df.copy()
    if class_of_business_filter != "All":
        filtered_df = filtered_df[filtered_df["Class of Business"] == class_of_business_filter]

    if class_type_filter != "All":
        if "," in class_type_filter:
            class_types = class_type_filter.split(",")
            filtered_df = filtered_df[filtered_df["ClassType"].isin(class_types)]
        else:
            filtered_df = filtered_df[filtered_df["ClassType"] == class_type_filter]

    filtered_df['Year'] = filtered_df['Year'].astype(str)
    grouped_df = filtered_df.groupby(['Year', 'Class of Business', 'ClassType']).agg(
        {'Earned Premium': 'sum', 'GWP': 'sum', 'Business Plan': 'sum'}).reset_index()

    return grouped_df

business_classes = list(class_df['Class of Business'].unique())
class_types = list(class_df['ClassType'].unique())

# Display filtered class data
business_class = st.selectbox('Choose Business Class', business_classes)
class_type = st.selectbox('Choose Class Type', class_types)

class_filtered = class_filter(class_df, business_class, class_type)
st.write(class_filtered.set_index(class_filtered.columns[0]))

# Draw bar chart for class data
def draw_bar_chart(df):
    years = df['Year'].unique()
    try:
        chart_cols = st.columns(len(years))
    except:
        pass
    for index, year in enumerate(years):
        year_data = df[df['Year'] == year]
        data_dict = {}
        for index, row in year_data.iterrows():
            key = f"{row['Class of Business']} - {row['ClassType']}"
            if key not in data_dict:
                data_dict[key] = {
                    'GWP': 0,
                    'Earned Premium': 0,
                    'Business Plan': 0
                }
            data_dict[key]['GWP'] += row['GWP']
            data_dict[key]['Earned Premium'] += row['Earned Premium']
            data_dict[key]['Business Plan'] += row['Business Plan']

        chart_data = pd.DataFrame(data_dict).T

        try:
            chart_cols[index].subheader(year)
            chart_cols[index].bar_chart(chart_data)
        except:
            st.write('No such data')

draw_bar_chart(class_filtered)
