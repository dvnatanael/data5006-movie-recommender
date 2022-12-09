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

from recommendation_system import get_recommendations, load_dataset


# %%
def fetch_movie_info(movie_id: int, links_df: pd.DataFrame, omdb_api_key: str) -> dict:
    # get the imdb_id for the given movid_id
    imdb_id = links_df.query("movieId == @movie_id")["imdbId"].squeeze()
    imdb_id = f"tt{imdb_id:07d}"

    # get the movie information from the OMDB API
    imdb_url = f"http://www.omdbapi.com/?apikey={omdb_api_key}&i={imdb_id}"
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
def main(omdb_api_key: str, *, data_dir: str | None = None) -> None:
    if data_dir is None:
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
        # select movie
        movie: str = st.selectbox(
            label="Select a Movie",
            options=movie_titles_df,
        )  # type: ignore

        with st.spinner("`Getting recommendations...`"):
            recommendations = get_recommendations(movie, user_movie_df)

        # show the top 5 recommendations
        max_recommendations = 5
        recommendation_count = 0
        for movie_id in recommendations.index:
            if recommendation_count == max_recommendations:
                break

            movie_info = fetch_movie_info(movie_id, links_df, omdb_api_key)
            if movie_info["Response"] == "True":
                show_movie_info(movie_info)
                recommendation_count += 1


# %%
if __name__ == "__main__":
    # load environment variables
    load_dotenv()
    omdb_api_key = os.getenv("OMDB_API_KEY")

    if omdb_api_key is None:
        raise ValueError(".env must contain OMDB_API_KEY")

    # download and extract the dataset if needed
    src_url = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
    data_dir = os.path.join(os.curdir, "data")
    if not (os.path.isdir(data_dir) and len(os.listdir(data_dir))):
        from fetch_dataset import download_and_extract

        download_and_extract(src_url, data_dir)

    main(omdb_api_key)
