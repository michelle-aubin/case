# name of sqlite database
DB_NAME = "cord19.db"

# parameters for BM25 ranking function
BM25_B = 0.3
BM25_K1 = 1.2
BM25_delta = 1

# parameter for term frequency function
TF_F0 = 0.2

# base url for json files of the documents in CORD-19 dataset
URL = "https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/latest/"

# separator used in .txt files to populate db
SEP = "|!|"