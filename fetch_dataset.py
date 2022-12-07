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
import zipfile
from urllib.request import urlretrieve


# %%
def download_and_extract(src_url: str, dest_path: str) -> None:
    # setup data folder
    download_dir = os.path.join(dest_path, "download")

    if not os.path.isdir(download_dir):
        os.makedirs(download_dir)

    # download the dataset
    filename = src_url[src_url.rfind("/") + 1 :]
    filepath = os.path.join(download_dir, filename)
    urlretrieve(src_url, filepath)

    # extract the dataset
    with zipfile.ZipFile(filepath, "r") as f:
        f.extractall(dest_path)


# %%
if __name__ == "__main__":
    src_url = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
    data_dir = os.path.join(os.curdir, "data")
    download_and_extract(src_url, data_dir)
