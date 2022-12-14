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
import tensorflow_probability as tfp

from constants import SECONDS_IN_A_DAY


# %%
@st.cache(ttl=SECONDS_IN_A_DAY, show_spinner=False)
def mean_center_ratings(df: pd.DataFrame) -> pd.Series:
    def damp_mean_ratings(df: pd.DataFrame) -> pd.Series:
        return df["num_ratings"] * df["mean_rating"] / (df["num_ratings"] + 4)

    damped_mean_rating = (
        df.groupby("movieId")
        .agg(
            num_ratings=pd.NamedAgg(column="rating", aggfunc=len),
            mean_rating=pd.NamedAgg(column="rating", aggfunc="mean"),
        )
        .pipe(damp_mean_ratings)
        .astype("float32")
        .to_frame(name="damped_mean_rating")
        .merge(df, how="right", left_index=True, right_on="movieId")
        .loc[:, "damped_mean_rating"]
    )
    return df["rating"] - damped_mean_rating


# %%
@st.cache(ttl=SECONDS_IN_A_DAY, show_spinner=False)
def user_item_interactions_matrix(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.assign(mean_centered_rating=mean_center_ratings)
        .pivot(index="userId", columns="movieId", values="mean_centered_rating")
        .fillna(0)
    )


# %%
@st.cache(ttl=SECONDS_IN_A_DAY, show_spinner=False)
def item_genre_interactions_matrix(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.loc[:, ["movieId", "genres"]]
        .drop_duplicates(keep="first", ignore_index=True)
        .assign(genres=lambda x: x["genres"].str.split("|"))
        .explode("genres")
        .pivot(values="genres", index="movieId", columns="genres")
        .notnull()
        .astype("uint8")
        .T
    )


# %%
@st.cache(ttl=SECONDS_IN_A_DAY, show_spinner=False)
def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    corr = tfp.stats.correlation(df.to_numpy(dtype="float16"))
    return pd.DataFrame(corr, columns=df.columns, index=df.columns)


# %%
@st.cache(ttl=SECONDS_IN_A_DAY, show_spinner=False)
def load_dataset(path: str) -> dict[str, pd.DataFrame]:
    def read_csv(filename: str) -> pd.DataFrame:
        return pd.read_csv(os.path.join(path, filename))

    ratings_df = read_csv("ratings.csv")
    movies_df = read_csv("movies.csv")
    tags_df = read_csv("tags.csv")
    links_df = read_csv("links.csv")

    # convert unix timestamps to datetime
    ratings_df["timestamp"] = pd.to_datetime(ratings_df["timestamp"], unit="s")
    tags_df["timestamp"] = pd.to_datetime(tags_df["timestamp"], unit="s")

    ratings_df["rating"] = ratings_df["rating"].astype("float32")

    movie_titles_df = movies_df["title"].squeeze().sort_values()  # type: ignore
    user_movie_df = pd.merge(ratings_df, movies_df, on="movieId")

    return {
        "ratings": ratings_df,
        "movies": movies_df,
        "links": links_df,
        "tags": tags_df,
        "movie titles": movie_titles_df,
        "user movie interactions": user_movie_df,
    }


# %%
# @st.cache(ttl=300, show_spinner=False)
def get_recommendations(title: str, user_movie_df: pd.DataFrame) -> pd.DataFrame:
    # get corresponding movie id
    movie_id = (
        user_movie_df.query("title == @title")["movieId"].drop_duplicates().squeeze()
    )

    # calculate interaction matrices
    user_movie_utility_matrix = user_item_interactions_matrix(user_movie_df)
    genre_movie_utility_matrix = item_genre_interactions_matrix(user_movie_df)

    # corr between 2 cols may be NA; mwe: [[0, 0], [0, 0]]
    user_movie_corr_df = correlation_matrix(user_movie_utility_matrix).fillna(0)
    genre_movie_corr_df = correlation_matrix(genre_movie_utility_matrix)

    # relative importance of genre correlation compared to user rating correlation
    alpha = 0.2
    corr_df = user_movie_corr_df + alpha * (genre_movie_corr_df - user_movie_corr_df)
    return (
        corr_df.loc[:, [movie_id]]
        .drop(index=movie_id)  # do not recommend the selected movie
        .sort_values(by=movie_id, ascending=False)  # type: ignore
    )
