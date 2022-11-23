from urllib.request import urlretrieve
import zipfile
import os
path = "data"
isExist = os.path.exists(path)
if not isExist:
   os.makedirs(path)
urlretrieve("https://files.grouplens.org/datasets/movielens/ml-latest-small.zip", "ml-latest-small.zip")
zip_ref = zipfile.ZipFile('ml-latest-small.zip', "r")
zip_ref.extractall("data")
os.remove('ml-latest-small.zip')

import pandas as pd 
movies = pd.read_csv(r"movies = pd.read_csv(r"/workspaces/data5006-movie-recommender/ml-latest-small/movies.csv")
movies")
tags = pd.read_csv(r"/workspaces/data5006-movie-recommender/ml-latest-small/tags.csv")
ratings = pd.read_csv(r"/workspaces/data5006-movie-recommender/ml-latest-small/ratings.csv")
links = pd.read_csv(r"/workspaces/data5006-movie-recommender/ml-latest-small/links.csv")
