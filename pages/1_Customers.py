import streamlit as st
import pandas as pd
from millify import millify
import plotly.express as px

st.set_page_config(
    page_title="Customers",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded")


# Load data with encoding specification
df_customers = pd.read_csv('df_customers.csv', encoding='ISO-8859-1')

col1, col2 = st.columns(2, gap='small')


# Define regions
regions = {
    'NORTH CENTRAL': ['Kogi', 'Kwara', 'Niger', 'Plateau', 'Benue', 'Nasarawa', 'FederalCapitalTerritory'], 
    'NORTH EAST': ['Adamawa', 'Bauchi', 'Borno', 'Gombe', 'Taraba', 'Yobe'],
    'NORTH WEST': ['Jigawa', 'Kaduna', 'Kano', 'Katsina', 'Kebbi', 'Sokoto', 'Zamfara'],
    'SOUTH EAST': ['Abia', 'Anambra', 'Ebonyi', 'Enugu', 'Imo'],
    'SOUTH SOUTH': ['AkwaIbom', 'Bayelsa', 'CrossRiver', 'Delta', 'Edo', 'Rivers'],
    'LAGOS': ['Lagos'],
    'SOUTH WEST': ['Ekiti', 'Ogun', 'Ondo', 'Osun', 'Oyo']
}


# Sidebar for user input
selected_region = st.sidebar.selectbox('Select Region', ['All'] + list(regions.keys()))
selected_year = st.sidebar.select_slider('Select a Year', sorted(df_customers['Year'].unique()), value=int(df_customers['Year'].max()-2))
selected_month = st.sidebar.selectbox('Select a Month', sorted(df_customers['Month'].unique()))
selected_customer = st.sidebar.selectbox('Select Customer', sorted(df_customers['CustomerName'].unique()))


# Filter data for the selected region, year, and month
if selected_region == 'All':
    filtered_data_ym = df_customers[(df_customers['Year'] == selected_year) & (df_customers['Month'] == selected_month)]
else:
    filtered_data_ym = df_customers[(df_customers['Region'] == selected_region) & (df_customers['Year'] == selected_year) & (df_customers['Month'] == selected_month)]

filtered_data_ym = filtered_data_ym.groupby('CustomerName')['MT lifted'].sum().reset_index()
top_customers_ym = filtered_data_ym.nlargest(10, 'MT lifted')


# Filter data for the selected region and year
if selected_region == 'All':
    filtered_data_y = df_customers[(df_customers['Year'] == selected_year)]
else:
    filtered_data_y = df_customers[(df_customers['Region'] == selected_region) & (df_customers['Year'] == selected_year)]

filtered_data_y = filtered_data_y.groupby('CustomerName')['MT lifted'].sum().reset_index()
top_customers_y = filtered_data_y.nlargest(5, 'MT lifted')


#NAME CARD FOR THE YEAR
change_df = df_customers[(df_customers['Year'] == selected_year) & (df_customers['CustomerName'] == selected_customer)]
change_df_value = change_df['MT lifted'].sum()

previous_change_df = df_customers[(df_customers['Year'] == (selected_year - 1)) & (df_customers['CustomerName'] == selected_customer)]
previous_change_df_value = previous_change_df['MT lifted'].sum()

delta_customer = (change_df_value) - (previous_change_df_value) 


#NAME CARD FOR THE MONTH
change_df_m = df_customers[(df_customers['Year'] == selected_year) & (df_customers['Month'] == selected_month) & (df_customers['CustomerName'] == selected_customer)]
change_df_m_value = change_df_m['MT lifted'].sum()

previous_change_df_m = df_customers[(df_customers['Year'] == (selected_year - 1)) & (df_customers['Month'] == selected_month) & (df_customers['CustomerName'] == selected_customer)]
previous_change_df_m_value = previous_change_df_m['MT lifted'].sum()

delta_customer_m = (change_df_m_value) - (previous_change_df_m_value)

#Line graph for customer historical performance
customer_chart = df_customers[(df_customers['CustomerName'] == selected_customer)]
customer_chart_df = customer_chart.groupby('Year')['MT lifted'].sum()

#All time record customer
all_time_customer = customer_chart['MT lifted'].sum()



with col1:
    fig_bar = px.bar(top_customers_y, x='MT lifted', y='CustomerName', orientation='h', title=f'Top 5 Customers in {selected_region} region(s) for year {selected_year}')
    st.plotly_chart(fig_bar)

with col2:
    fig_bar = px.bar(top_customers_ym, x='MT lifted', y='CustomerName', orientation='h', title=f'Top 10 Customers in {selected_region} region(s) for year {selected_year} month {selected_month}')
    st.plotly_chart(fig_bar)

st.write(f'Selected Customer: {selected_customer}')
col1, col2, col3= st.columns(3)
col1.metric(label=f" Sales in {selected_year}", 
          value=millify(change_df_value, precision=2), 
          delta=millify(delta_customer, precision=2), 
          help= "The indicator below shows performance against PY")
col2.metric(label=f" Sales in month {selected_month} of {selected_year}", 
          value=millify(change_df_m_value, precision=2), 
          delta=millify(delta_customer_m, precision=2),
          help="The indicator below shows performance against same month PY")
col3.metric(label='Last 10 years record',
            value=millify(all_time_customer),
            delta=None,
            help='There is no indicator for this metric')

col = st.columns((1.5, 4.5), gap='small')
with col[0]:
    st.write('Breakdown of last 10 years')
    st.write(customer_chart_df)
with col[1]:
    st.write(f'{selected_customer}\'s trend')
    st.area_chart(customer_chart_df)