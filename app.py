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
        movie = st.selectbox(label="Select a Movie", options=movies_df["title"])
        movie_id = movies_df.loc[movies_df["title"] == movie, "movieId"].iloc[0]

        # fetch movie info
        imdb_id = f"tt0{links_df.query('movieId == @movie_id')['imdbId'].iloc[0]}"

        url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={omdb_api}"
        movie_info = requests.get(url).json()

        # show movie info
        raw_df = pd.merge(ratings_df, movies_df, on="movieId")
        utility_matrix = get_utility_matrix(raw_df)

        corr_df = calculate_movie_rating_similarity(utility_matrix)
        top20 = corr_df[movie_id].sort_values(ascending=False).iloc[1:21]
        movies_df.set_index("movieId").loc[top20.index, "title"].reset_index(drop=True)

        new_movies_df = movies_df.assign(
            genres=lambda x: x.genres.str.split("|")
        ).explode("genres")
        movies = (
            new_movies_df.pivot(
                values="genres", index=["movieId", "title"], columns="genres"
            )
            .notnull()
            .astype("int")
        )

        corr_df_2 = movies.T.corr()
        st.write(corr_df_2.loc[:, 100].squeeze().sort_values(ascending=False).iloc[:20])

        poster_container, plot_container = st.columns([1, 2])
        if movie_info["Response"] == "True":
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

    main(omdb_api)
