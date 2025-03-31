import streamlit as st
import geopandas as gpd
import pandas as pd
import numpy as np
import plotly.graph_objects as go

def load_geopackage(file):
    try:
        gdf = gpd.read_file(file)
        return gdf
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

def compute_upl(blocks, value_col, cost_col):
    """Compute UPL using user-selected columns."""
    if value_col not in blocks.columns or cost_col not in blocks.columns:
        st.error("Invalid column selection. Please check your dataset.")
        return blocks
    
    blocks["profit"] = blocks[value_col] - blocks[cost_col]
    blocks["in_pit"] = blocks["profit"] > 0  # Mark profitable blocks
    return blocks

def plot_3d(blocks):
    """Plot UPL result in 3D using Plotly."""
    fig = go.Figure()
    
    in_pit = blocks[blocks["in_pit"]]
    out_pit = blocks[~blocks["in_pit"]]
    
    fig.add_trace(go.Scatter3d(
        x=in_pit.geometry.x, y=in_pit.geometry.y, z=in_pit.geometry.z,
        mode='markers', marker=dict(size=3, color='red'),
        name='In Pit'
    ))
    
    fig.add_trace(go.Scatter3d(
        x=out_pit.geometry.x, y=out_pit.geometry.y, z=out_pit.geometry.z,
        mode='markers', marker=dict(size=2, color='blue'),
        name='Out of Pit'
    ))
    
    fig.update_layout(title="Ultimate Pit Limit Visualization", margin=dict(l=0, r=0, b=0, t=40))
    st.plotly_chart(fig)

st.title("Ultimate Pit Limit (UPL) Analysis")

uploaded_file = st.file_uploader("Upload GeoPackage Block Model", type=["gpkg"])

if uploaded_file:
    blocks = load_geopackage(uploaded_file)
    if blocks is not None:
        st.write("## Block Model Preview")
        st.write(blocks.head())

        # Allow user to select the columns for 'value' and 'cost'
        value_column = st.selectbox("Select the 'value' column:", blocks.columns)
        cost_column = st.selectbox("Select the 'cost' column:", blocks.columns)

        if st.button("Compute UPL"):
            blocks = compute_upl(blocks, value_column, cost_column)
            st.success("UPL Computation Completed!")
            st.write(blocks.head())  # Display updated data
            plot_3d(blocks)
