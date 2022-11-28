# ---
# jupyter:
#   jupytext:
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
import tensorflow as tf


# %%
data_dir = os.path.join(".", "data", "ml-latest-small")

ratings_df = pd.read_csv(os.path.join(data_dir, "ratings.csv"))
ratings_df["timestamp"] = pd.to_datetime(
    ratings_df["timestamp"], unit="s", origin="unix"
)

movies_df = pd.read_csv(os.path.join(data_dir, "movies.csv"))

tags_df = pd.read_csv(os.path.join(data_dir, "tags.csv"))
tags_df["timestamp"] = pd.to_datetime(tags_df["timestamp"], unit="s", origin="unix")

raw_df = pd.merge(ratings_df, movies_df, on="movieId")
raw_df

# %%
df = (
    raw_df.groupby("movieId")
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
df = raw_df.join(df, on="movieId").assign(
    mean_centered_rating=lambda x: x["rating"] - x["mean_rating"]
)
df  # type: ignore

# %%
data_table = df.pivot(
    index="userId", columns="movieId", values="mean_centered_rating"
).fillna(0)
data_table.tail()

# %%
corr_df = data_table.corr()

# %%
corr_df.loc[:, 10].sort_values(ascending=False).head(20)

# %%
A, B = ["xXx (2002)", "Star Wars: Episode II - Attack of the Clones (2002)"]
-tf.losses.cosine_similarity(data_table[A], data_table[B]).numpy()  # type: ignore

# %%
data_table.loc[(abs(data_table[A]) > 1e-4) & (abs(data_table[B]) > 1e-4), [A, B]]
