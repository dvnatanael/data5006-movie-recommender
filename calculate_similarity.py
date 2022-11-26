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


# %%
data_dir = os.path.join(".", "data", "ml-latest-small")
df1 = pd.read_csv(os.path.join(data_dir, "ratings.csv"))
df2 = pd.read_csv(os.path.join(data_dir, "movies.csv"))
data = df1.merge(df2, on="movieId")

# %%
data

# %%
data_table = pd.pivot_table(data, values="rating", columns="title", index="userId")
data_table.tail()

# %%
print(
    "here are a list of 20 movies to recommend to a user who has liked '101 Dalmatians (1996)'"
)
table_corr = pd.DataFrame(
    data_table.corr()["101 Dalmatians (1996)"].sort_values(ascending=False).iloc[:20]
)
table_corr
