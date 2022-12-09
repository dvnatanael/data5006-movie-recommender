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
import requests
import streamlit as st
from dotenv import load_dotenv

from constants import SECONDS_IN_A_DAY
from similarity import (
    correlation_matrix,
    item_genre_interactions_matrix,
    user_item_interactions_matrix,
)


# %%
@st.cache(ttl=SECONDS_IN_A_DAY)
def load_dataset(path: str) -> tuple:
    def read_csv(filename: str) -> pd.DataFrame:
        return pd.read_csv(os.path.join(path, filename))

    ratings_df = read_csv("ratings.csv")
    movies_df = read_csv("movies.csv")
    tags_df = read_csv("tags.csv")
    links_df = read_csv("links.csv")

    # convert unix timestamps to datetime
    ratings_df["timestamp"] = pd.to_datetime(ratings_df["timestamp"], unit="s")
    tags_df["timestamp"] = pd.to_datetime(tags_df["timestamp"], unit="s")

    return ratings_df, movies_df, links_df, tags_df


# %%
@st.cache(ttl=300)
def get_recommendations(title: str, user_movie_df: pd.DataFrame) -> pd.DataFrame:
    # get corresponding movie id
    movie_id = (
        user_movie_df.query("title == @title")["movieId"].drop_duplicates().squeeze()
    )

    # show movie info
    user_movie_utility_matrix = user_item_interactions_matrix(user_movie_df)
    genre_movie_utility_matrix = item_genre_interactions_matrix(user_movie_df)

    # corr between 2 cols may be NA; mwe: [[0, 0], [0, 0]]
    user_movie_corr_df = correlation_matrix(user_movie_utility_matrix).fillna(0)
    genre_movie_corr_df = correlation_matrix(genre_movie_utility_matrix)

    alpha = 0.2
    corr_df = user_movie_corr_df + alpha * (genre_movie_corr_df - user_movie_corr_df)
    return (
        corr_df.loc[:, [movie_id]]
        .drop(index=movie_id)  # do not recommend the selected movie
        .sort_values(by=movie_id, ascending=False)
    )


# %%
def fetch_movie_info(movie_id: int, links_df: pd.DataFrame, omdb_api_key: str) -> dict:
    imdb_id = links_df.query("movieId == @movie_id")["imdbId"].squeeze()
    imdb_url = f"http://www.omdbapi.com/?i=tt{imdb_id:07d}&apikey={omdb_api_key}"

    return requests.get(imdb_url).json()


# %%
def show_movie_info(movie_info: dict) -> None:
    poster_container, plot_container = st.columns([1, 2])
    with poster_container:
        st.image(movie_info["Poster"])
    with plot_container:
        st.subheader(movie_info["Title"])

        # streamlit write magic
        f"Released: {movie_info['Released']}"
        f"Duration: {movie_info['Runtime']}"
        movie_info["Plot"]


# %%
def main(omdb_api_key: str) -> None:
    data_dir = os.path.join(".", "data", "ml-latest-small")

    # load the data
    ratings_df, movies_df, links_df, tags_df = load_dataset(data_dir)
    movie_titles_df = movies_df["title"].squeeze().sort_values()
    user_movie_df = pd.merge(ratings_df, movies_df, on="movieId")

    # create website layout
    header = st.container()
    body = st.container()

    with header:
        st.title("Premiere Movies Catered Just for You")

    with body:
        # select movies
        movie: str = st.selectbox(
            label="Select a Movie",
            options=movie_titles_df,
        )  # type: ignore

        recommendations = get_recommendations(movie, user_movie_df)

        recommendation_count = 0
        for movie_id in recommendations.index:
            if recommendation_count == 5:
                break

            movie_info = fetch_movie_info(movie_id, links_df, omdb_api_key)
            if movie_info["Response"] == "True":
                show_movie_info(movie_info)
                recommendation_count += 1


# %%
if __name__ == "__main__":
    load_dotenv()
    omdb_api_key = os.getenv("OMDB_API_KEY")
    if omdb_api_key is None:
        raise ValueError(".env must contain OMDB_API_KEY")

    src_url = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
    data_dir = os.path.join(os.curdir, "data")
    if not (os.path.isdir(data_dir) and len(os.listdir(data_dir))):
        from fetch_dataset import download_and_extract

        download_and_extract(src_url, data_dir)

    main(omdb_api_key)
