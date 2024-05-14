import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.title("COMET Data Analysis")

# Sidebar for file upload and options
st.sidebar.title("Options")

# Upload file
uploaded_file = st.sidebar.file_uploader("Choose a file", type=['tsv'])

if uploaded_file is not None:
    # Read data
    df = pd.read_csv(uploaded_file, sep='\t', header=0)

    choices = df.columns
    # Exclude the columns starting with Study level or Name or X or Y or Image
    choices = [c for c in choices if 
               not c.startswith('Study level') and 
               not c.startswith('Distance') and 
               not c.startswith('Area') and 
               not c.startswith('LayerData') and
               not c.startswith('Name') and 
               not c.startswith('X') and 
               not c.startswith('Y') and 
               not c.startswith('Image')]

    # Allow user to select the marker to plot
    marker_choice = st.sidebar.selectbox("Select the marker to plot", choices)

    # Allow user to change figure dimensions
    fig_width = st.sidebar.number_input("Figure width", value=10)
    fig_height = st.sidebar.number_input("Figure height", value=10)

    # Allow user to change the size of the dots
    dot_size = st.sidebar.number_input("Dot size", value=5.0, step=0.5)

    # Set x and y limits
    x_min, x_max = df['X'].min(), df['X'].max()
    y_min, y_max = df['Y'].min(), df['Y'].max()

    if pd.api.types.is_numeric_dtype(df[marker_choice]):
        # Handle continuous variable
        # Use IQR to detect outliers and set min and max
        Q1 = df[marker_choice].quantile(0.25)
        Q3 = df[marker_choice].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        min_val = st.sidebar.number_input("Set minimum value for the scale", value=float(max(df[marker_choice].min(), lower_bound)))
        max_val = st.sidebar.number_input("Set maximum value for the scale", value=float(min(df[marker_choice].max(), upper_bound)))
        
        filtered_df = df[(df[marker_choice] >= min_val) & (df[marker_choice] <= max_val)]
        
        fig = px.scatter(filtered_df, x='X', y='Y', color=marker_choice, color_continuous_scale='Viridis', size_max=dot_size)
        fig.update_layout(xaxis_title='X', yaxis_title='Y', width=fig_width*100, height=fig_height*100)
    else:
        # Handle categorical variable
        categories = pd.Categorical(df[marker_choice]).codes
        cmap = px.colors.qualitative.Safe
        color_map = {k: cmap[i % len(cmap)] for i, k in enumerate(set(categories))}
        fig = px.scatter(df, x='X', y='Y', color=df[marker_choice], category_orders={marker_choice: sorted(df[marker_choice].unique())}, color_discrete_map=color_map, size_max=dot_size)
        fig.update_layout(xaxis_title='X', yaxis_title='Y', width=fig_width*100, height=fig_height*100)
        
        # Add legend
        fig.update_layout(legend_title_text='Levels')

    # Set fixed x and y limits
    fig.update_xaxes(range=[x_min, x_max], showticklabels=False, title='')
    fig.update_yaxes(range=[y_min, y_max], showticklabels=False, title='')

    st.plotly_chart(fig)
