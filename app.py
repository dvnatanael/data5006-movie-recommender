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

from utils import calculate_movie_rating_similarity, get_utility_matrix


# %%
def main():
    data_dir = os.path.join(".", "data", "ml-latest-small")

    # load the data
    ratings_df = pd.read_csv(os.path.join(data_dir, "ratings.csv"))
    movies_df = pd.read_csv(os.path.join(data_dir, "movies.csv"))
    tags_df = pd.read_csv(os.path.join(data_dir, "tags.csv"))

    # convert unix timestamps to datetime
    ratings_df["timestamp"] = pd.to_datetime(ratings_df["timestamp"], unit="s")
    tags_df["timestamp"] = pd.to_datetime(tags_df["timestamp"], unit="s")

    raw_df = pd.merge(ratings_df, movies_df, on="movieId")
    utility_matrix = get_utility_matrix(raw_df)

    # create website layout
    header = st.container()
    dataset = st.container()

    with header:
        st.title("Premiere Movie Cater Just for You")

    with dataset:
        movie = st.selectbox(
            label="Select a Movie",
            options=movies_df["title"],
        )
        movie_id = movies_df.loc[movies_df["title"] == movie, "movieId"].iloc[0]

    corr_df = calculate_movie_rating_similarity(utility_matrix)
    top20 = corr_df[movie_id].sort_values(ascending=False).iloc[1:21]
    movies_df.set_index("movieId").loc[top20.index, "title"].reset_index(drop=True)


# %%
if __name__ == "__main__":
    main()
