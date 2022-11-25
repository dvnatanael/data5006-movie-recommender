# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
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
def download_and_extract(src_url: str, data_dir: str) -> None:
    # setup data folder
    download_dir = os.path.join(data_dir, "download")

    if not os.path.isdir(download_dir):
        os.makedirs(download_dir)

    # download the dataset
    zip_path = os.path.join(download_dir, src_url[src_url.rfind("/") + 1 :])
    urlretrieve(src_url, zip_path)

    # extract the dataset
    with zipfile.ZipFile(zip_path, "r") as f:
        f.extractall(data_dir)


# %%
if __name__ == "__main__":
    src_url = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
    data_dir = os.path.join(os.curdir, "data")
    download_and_extract(src_url, data_dir)
