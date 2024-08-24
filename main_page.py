import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
from millify import millify


st.set_page_config(
    page_title="NASCON Sales Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded")


# Load GeoJSON files
nigeria = gpd.read_file('Nigeria.json')
nigeria_boundary = gpd.read_file('nigeria_boundary.geojson')

# Create regions
regions = {
    'NORTH CENTRAL': ['Kogi', 'Kwara', 'Niger', 'Plateau', 'Benue', 'Nasarawa', 'FederalCapitalTerritory'], 
    'NORTH EAST': ['Adamawa', 'Bauchi', 'Borno', 'Gombe', 'Taraba', 'Yobe'],
    'NORTH WEST': ['Jigawa', 'Kaduna', 'Kano', 'Katsina', 'Kebbi', 'Sokoto', 'Zamfara'],
    'SOUTH EAST': ['Abia', 'Anambra', 'Ebonyi', 'Enugu', 'Imo'],
    'SOUTH SOUTH': ['AkwaIbom', 'Bayelsa', 'CrossRiver', 'Delta', 'Edo', 'Rivers'],
    'LAGOS': ['Lagos'],
    'SOUTH WEST': ['Ekiti', 'Ogun', 'Ondo', 'Osun', 'Oyo']
}

# Create a new column for region in Nigeria dataframe
nigeria['Region'] = 'Other'  # Default value
for region, states in regions.items():
    nigeria.loc[nigeria['NAME_1'].isin(states), 'Region'] = region

# Sample data (replace 'df2.csv' with your actual CSV filename)
data_df = pd.read_csv('df2.csv')

# Streamlit app
st.title("NASCON SALES DATA VISUALIZATION APP")
st.markdown("""
This application visualizes the distribution of various NASCON sales across different regions in Nigeria. 
Use the side bar options to customize the map and view specific regions.
""")

col = st.columns((1.5, 4.5), gap='small')

# Sidebar for region selection
selected_region = st.sidebar.selectbox('Select a Region', ['All'] + list(regions.keys()))
selected_year = st.sidebar.select_slider('Select a Year', sorted(data_df['Year'].unique()), value=int(data_df['Year'].max()-1))
#selected_year = st.sidebar.selectbox('Select a Year', sorted(data_df['Year'].unique()))
selected_month = st.sidebar.selectbox('Select a Month', sorted(data_df['Month'].unique()))

st.sidebar.success("Select any page above for further analysis.")

with col[1]:
    # Display selected filters
    st.subheader(f"Region: {selected_region}, Year: {selected_year}, Month: {selected_month}")

    # Filter data for the selected region, year, and month
    if selected_region == 'All':
        filtered_data = data_df[(data_df['Year'] == selected_year) & (data_df['Month'] == selected_month)]
    else:
        filtered_data = data_df[(data_df['Region'] == selected_region) & (data_df['Year'] == selected_year) & (data_df['Month'] == selected_month)]

    # Calculate total Tonnes for selected region, year, and month
    #st.write(f"Region: {selected_region}, Year: {selected_year}, Month: {selected_month}")
    total_tonnes = filtered_data['Tonnes'].sum()

    # Display total Tonnes
    st.write(f"Total tonnes achieved in {selected_region} region(s): {total_tonnes}")

    # Create folium map
    map_nigeria = folium.Map(location=[9.0820, 8.6753], zoom_start=6, tiles='CartoDB positron', control_scale=True)

    # Add Nigeria's boundary to the map
    folium.GeoJson(
        nigeria_boundary,
        name='Nigeria Boundary',
        style_function=lambda x: {'color': 'black', 'weight': 2, 'fillOpacity': 0}
    ).add_to(map_nigeria)

    # Add selected region's boundaries to the map
    if selected_region != 'All':
        folium.GeoJson(
            nigeria[nigeria['Region'] == selected_region],
            name='Selected Region'
        ).add_to(map_nigeria)

    # Add Choropleth layer
    if not filtered_data.empty:
        folium.Choropleth(
            geo_data=nigeria,
            #data=filtered_data,
            data=filtered_data.groupby('Region')['Tonnes'].sum(),
            columns=['Region', 'Tonnes'],  # Adjust columns based on your CSV structure
            key_on='feature.properties.Region',
            fill_color='RdYlBu',
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name='Tonnes'
        ).add_to(map_nigeria)

    # Display map in Streamlit
    folium_static(map_nigeria)


# Delta Year Only
previous_data_year_only = data_df[(data_df['Year'] == (selected_year -1))]
filtered_data_year_only = data_df[(data_df['Year'] == (selected_year))]
delta_year_only = ((filtered_data_year_only['Tonnes'].sum()) - (previous_data_year_only['Tonnes'].sum()))

# Delta Year and Month
previous_data_year_month = data_df[(data_df['Year'] == (selected_year -1)) & (data_df['Month'] == selected_month)]
filtered_data_year_month = data_df[(data_df['Year'] == (selected_year)) & (data_df['Month'] == selected_month)]
delta_year_month = ((filtered_data_year_month['Tonnes'].sum()) - (previous_data_year_month['Tonnes'].sum()))

# Delta Month Only(with focus on Month -1)
previous_data_month_focus = data_df[(data_df['Year'] == (selected_year)) & (data_df['Month'] == (selected_month - 1))]
filtered_data_month_focus = data_df[(data_df['Year'] == (selected_year)) & (data_df['Month'] == (selected_month))]
delta_month_focus = ((filtered_data_month_focus['Tonnes'].sum()) - (previous_data_month_focus['Tonnes'].sum()))


with col[0]:
    st.metric(label=f" Global Sales in {selected_year}",
              value=millify(filtered_data_year_only['Tonnes'].sum(), precision=2),
              delta=millify(delta_year_only, precision=2))
    st.metric(label=f" Sales in month {selected_month} against {selected_year-1}",
              value=millify(filtered_data_year_month['Tonnes'].sum(), precision=2),
              delta=millify(delta_year_month, precision=2))
    st.metric(label="Sales against prior month",
              value=millify(filtered_data_month_focus['Tonnes'].sum(), precision=2),
              delta=millify(delta_month_focus, precision=2))
    st.markdown("""
    Regional Breakdown
        """)
    st.write(filtered_data.groupby('Region')['Tonnes'].sum())