import streamlit as st
import pandas as pd
import numpy as np
import google.generativeai as genai

broker_df = pd.read_excel('./data/2024 Dashboard Data.xlsx', sheet_name='Broker stats')
class_df = pd.read_excel('./data/2024 Dashboard Data.xlsx', sheet_name='Class stats')

# Configure AI model
genai.configure(api_key='AIzaSyCXnLt0axHYvQ9dDLHltCWY1UaOTTxmvPU')
model = genai.GenerativeModel('gemini-pro')

# Function to get response from AI model
def respond(msg):
    return model.generate_content(
        msg + 'table1' + broker_df.to_csv(index=False) + 'table2' + class_df.to_csv(index=False)).text

# Set up the page layout
st.set_page_config(layout="wide")
st.sidebar.title("Gemini Powered NLP Bot")
st.sidebar.markdown('''Disclaimer: If you don't get the expected answer try sending query again''')

# User input
user_input = st.sidebar.text_area("Your query:", height=300)

# Send button
if st.sidebar.button("Send"):
    bot_response = respond(user_input)
    st.sidebar.subheader("Answer")
    st.sidebar.write(bot_response)

# Dashboard title
st.title('Brokers, Premiums and Business Dashboard')

# Top 10 Brokers section
st.subheader('Top 10 Brokers Performance')
menu_col, table_col, gwp_graph_col = st.columns([1, 2, 2])

# Dropdown for market types and years
market_type = menu_col.selectbox('Select Market Type', options=['Open Market', 'Facilities', 'Combined'])
year = menu_col.selectbox('Select Year', options=years)

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
    # grouped_df.drop(columns='Year', inplace=True)
    grouped_df['Success Rate (%)'] = ((grouped_df['Planned GWP'] - grouped_df['GWP']) / grouped_df['Planned GWP']) * 100
    return grouped_df.head(10)


with menu_col:
    market_type = st.selectbox('Choose Market Type', market_types)
    year = st.selectbox('Choose Year', years)
with table_col:
    filtered_data = filter_and_group(broker_df, year, market_type)
    # print(filtered_data)
    st.write(
        filtered_data[['Broker Name', 'GWP', 'Planned GWP', 'Success Rate (%)']].set_index(filtered_data.columns[0]))
with gwp_graph_col:
    st.bar_chart(data=filtered_data, x='Broker Name', y='GWP')

st.subheader('Business Case Analysis')

business_classes = list(class_df['Class of Business'].unique())
class_types = list(class_df['ClassType'].unique())

class_menu_col, class_graph_col = st.columns([1, 3])


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


with class_menu_col:
    business_class = st.selectbox('Choose Business Class', business_classes)
    class_type = st.selectbox('Choose Class Type', class_types)


def draw_bar_chart(df):
    years = df['Year'].unique()
    try:
        chart_cols = st.columns(len(years))
        # break
    except:
        pass
    for year in years:

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


with class_graph_col:
    class_filtered = class_filter(class_df, business_class, class_type)
    st.write(class_filtered.set_index(class_filtered.columns[0]))
    # st.title('Bar Chart')
    draw_bar_chart(class_filtered)
