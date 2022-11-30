# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all,lines_to_next_cell
#     formats: ipynb,py:percent
#     notebook_metadata_filter: -kernelspec
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.14.1
# ---

# %%
import os

import pandas as pd
import streamlit as st


# %%
header = st.container()
dataset = st.container()

# %%
with header:
    st.title("Premiere Movie Cater Just for You")

# %%
with dataset:
    df = pd.read_csv(os.path.join(os.curdir, "data", "ml-latest-small", "movies.csv"))
    movie = st.selectbox(
        label="Select a Movie",
        options=df["title"],
    )
    df.query("title == @movie")["movieId"].iloc[0]
