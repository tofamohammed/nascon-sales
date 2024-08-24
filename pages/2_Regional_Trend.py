import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

st.set_page_config(
    page_title="Regional trend",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded")


# Load data with encoding specification
df = pd.read_csv('df2.csv', encoding='ISO-8859-1')
df3 = pd.read_csv('df3.csv', encoding='ISO-8859-1')  # Load df3 for additional filtering


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
selected_region = st.sidebar.selectbox('Select Region', list(regions.keys()))
selected_year = st.sidebar.select_slider('Select a Year', sorted(df3['Year'].unique()), value=int(df3['Year'].max()-1))
selected_month = st.sidebar.selectbox('Select Month', df3['Month'].unique())
comparison_years = st.sidebar.multiselect('Select Comparison Years', df3['Year'].unique(), default=[selected_year - 1])
material_description = st.sidebar.selectbox('Select Material Description', df3['Material Description'].unique())


# Filter data based on user input for line plot
filtered_df = df[(df['Region'] == selected_region) & (df['Year'] == selected_year)]
filtered_year_df=df[(df['Year'] == selected_year)]
year_only_df=filtered_year_df.groupby('Year')['Tonnes'].sum()

# Filter df3 for time series plot
filtered_df3 = df3[(df3['Region'] == selected_region) & (df3['Year'] == selected_year) & (df3['Month'] == selected_month) & (df3['Material Description'] == material_description)]
filtered_df3['Actual PGI Date'] = pd.to_datetime(filtered_df3['Actual PGI Date'])
grouped_df3 = filtered_df3.groupby('Actual PGI Date')['Delivery Quantity (Tonnes)'].sum().reset_index()


# Create line plot
#st.subheader('Regional Trend')
monthly_tonnes = filtered_df.groupby('Month')['Tonnes'].sum().reset_index()
fig_line = go.Figure()
fig_line.add_trace(go.Scatter(x=monthly_tonnes['Month'], y=monthly_tonnes['Tonnes'], mode='lines+markers', name=f'{selected_year}'))

for comp_year in comparison_years:
    df_comp_year = df[(df['Region'] == selected_region) & (df['Year'] == comp_year)]
    comp_monthly_tonnes = df_comp_year.groupby('Month')['Tonnes'].sum().reset_index()
    fig_line.add_trace(go.Scatter(x=comp_monthly_tonnes['Month'], y=comp_monthly_tonnes['Tonnes'], mode='lines+markers', name=f'{comp_year}', line=dict(dash='dash')))

fig_line.update_layout(
    title=f'{selected_region} Regional Trend for {selected_year} and Comparison Years',
    xaxis_title='Month',
    yaxis_title='Tonnes'
)
st.plotly_chart(fig_line)


# Display time series for selected month and material description
col = st.columns((2, 5), gap='small')
with col[1]:
    fig_time_series = px.area(grouped_df3, x='Actual PGI Date', y='Delivery Quantity (Tonnes)', title=f'{material_description} sales in {selected_region} during month {selected_month}, {selected_year}')
    fig_time_series.update_xaxes(tickangle=45)
    st.plotly_chart(fig_time_series)
with col[0]:
    st.write(f'{material_description} breakdown')
    st.write(grouped_df3)
