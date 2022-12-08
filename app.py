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

from utils import calculate_movie_rating_similarity, get_utility_matrix


# %%
def main(omdb_api: str):
    data_dir = os.path.join(".", "data", "ml-latest-small")

    # load the data
    ratings_df = pd.read_csv(os.path.join(data_dir, "ratings.csv"))
    movies_df = pd.read_csv(os.path.join(data_dir, "movies.csv"))
    tags_df = pd.read_csv(os.path.join(data_dir, "tags.csv"))
    links_df = pd.read_csv(os.path.join(data_dir, "links.csv"))

    # convert unix timestamps to datetime
    ratings_df["timestamp"] = pd.to_datetime(ratings_df["timestamp"], unit="s")
    tags_df["timestamp"] = pd.to_datetime(tags_df["timestamp"], unit="s")

    # create website layout
    header = st.container()
    body = st.container()

    with header:
        st.title("Premiere Movies Catered Just for You")

    with body:
        # select movies
        movie = st.selectbox(
            label="Select a Movie",
            options=movies_df["title"].squeeze().sort_values(),
        )
        movie_id = movies_df.loc[movies_df["title"] == movie, "movieId"].iloc[0]

        # show movie info
        raw_df = pd.merge(ratings_df, movies_df, on="movieId")
        utility_matrix = get_utility_matrix(raw_df)

        movies = (
            movies_df.assign(genres=lambda x: x["genres"].str.split("|"))
            .explode("genres")
            .pivot(values="genres", index="movieId", columns="genres")
            .notnull()
            .astype("int")
            .T
        )
        # corr between 2 cols may be NA; mwe: [[0, 0], [0, 0]]
        corr_df_1 = calculate_movie_rating_similarity(utility_matrix).fillna(0)
        corr_df_2 = calculate_movie_rating_similarity(movies)

        alpha = 0.2
        corr_df = corr_df_1 + alpha * (corr_df_2 - corr_df_1)
        recommendations = corr_df[[movie_id]].sort_values(by=movie_id, ascending=False)

        recommendation_count = 0
        # do not recommend the selected movie
        for movie_id in recommendations.index[1:]:
            if recommendation_count == 5:
                break

            poster_container, plot_container = st.columns([1, 2])

            # fetch movie info
            recommended_movie_imdbid = links_df.loc[
                links_df["movieId"] == movie_id, "imdbId"
            ].iloc[0]

            imdb_id = f"tt{recommended_movie_imdbid:07d}"
            url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={omdb_api}"
            movie_info = requests.get(url).json()

            if movie_info["Response"] == "True":
                recommendation_count += 1
                with poster_container:
                    st.image(movie_info["Poster"])
                with plot_container:
                    st.subheader(movie_info["Title"])
                    f"Released: {movie_info['Released']}"
                    f"Duration: {movie_info['Runtime']}"
                    movie_info["Plot"]


# %%
if __name__ == "__main__":
    load_dotenv()
    omdb_api = os.getenv("OMDB_API")
    if omdb_api is None:
        raise ValueError(".env must contain OMDB API key")

    data_dir = os.path.join(os.curdir, "data")
    if not (os.path.isdir(data_dir) and len(os.listdir(data_dir))):
        from fetch_dataset import download_and_extract

        src_url = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
        download_and_extract(src_url, data_dir)

    main(omdb_api)
