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

from constants import SECONDS_IN_A_DAY


# %%
@st.cache(ttl=SECONDS_IN_A_DAY)
def user_item_interactions_matrix(df: pd.DataFrame) -> pd.DataFrame:
    def damp_mean_ratings(df: pd.DataFrame) -> pd.Series:
        return df["num_ratings"] * df["mean_rating"] / (df["num_ratings"] + 4)

    def mean_center_ratings(df: pd.DataFrame) -> pd.Series:
        return df["rating"] - df["damped_mean_rating"]

    df_statistics = (
        df.groupby("movieId")
        .agg(
            num_ratings=pd.NamedAgg(column="rating", aggfunc=len),
            mean_rating=pd.NamedAgg(column="rating", aggfunc="mean"),
        )
        .assign(damped_mean_rating=damp_mean_ratings)
    )
    return (
        df.join(df_statistics, on="movieId")
        .assign(mean_centered_rating=mean_center_ratings)
        .pivot(index="userId", columns="movieId", values="mean_centered_rating")
        .fillna(0)
    )


# %%
@st.cache(ttl=SECONDS_IN_A_DAY)
def item_genre_interactions_matrix(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.loc[:, ["movieId", "genres"]]
        .drop_duplicates(keep="first", ignore_index=True)
        .assign(genres=lambda x: x["genres"].str.split("|"))
        .explode("genres")
        .pivot(values="genres", index="movieId", columns="genres")
        .notnull()
        .astype("int")
        .T
    )


# %%
@st.cache(ttl=SECONDS_IN_A_DAY)
def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    return df.corr()
