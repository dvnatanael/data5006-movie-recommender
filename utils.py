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
import pandas as pd
import streamlit as st


# %%
@st.cache(ttl=86400)
def get_utility_matrix(df: pd.DataFrame) -> pd.DataFrame:
    new_df = (
        df.groupby("movieId")
        .agg(
            **{
                "num_ratings": pd.NamedAgg(column="rating", aggfunc=len),
                "mean_rating": pd.NamedAgg(column="rating", aggfunc=pd.DataFrame.mean),
            }
        )
        .assign(
            mod_mean_rating=lambda x: x["num_ratings"]
            * x["mean_rating"]
            / (x["num_ratings"] + 4)
        )
    )
    return (
        df.join(new_df, on="movieId")
        .assign(mean_centered_rating=lambda x: x["rating"] - x["mean_rating"])
        .pivot(index="userId", columns="movieId", values="mean_centered_rating")
        .fillna(0)
    )


# %%
@st.cache(ttl=86400)
def calculate_movie_rating_similarity(df: pd.DataFrame) -> pd.DataFrame:
    return df.corr()
