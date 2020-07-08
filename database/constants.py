# name of sqlite database
DB_NAME = "cord19.db"
# total num of docs in the database
TOTAL_DOCS = 73861
# average document length in words
AVG_DOC_LENGTH = 4434

# parameters for BM25 ranking function
BM25_B = 0.1
BM25_K1 = 0.1
BM25_delta = 1


# base url for json files of the documents in CORD-19 dataset
URL = "https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/latest/"

# separator used in .txt files to populate db
SEP = "|!|"