# parameters for BM25 ranking function
BM25_B = 0.3
BM25_K1 = 1.2
BM25_delta = 1

# parameters for proximity score function
PROX_K = 20
PROX_R = 0.75

# the num of docs from the posting lists to rank 
DOCS_K = 25

# base url for json files of the documents in CORD-19 dataset
URL = "https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/latest/"

# separator used in .txt files to populate db
SEP = "|!|"