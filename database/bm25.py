import sqlite3
import math
from constants import BM25_B, BM25_K1, BM25_delta

# Calculates and returns the summand for one query term of bm25 formula
# tf: the term frequency of the term in the doc
# idf: the inverse document frequency of the term
# doc_length: the length of the doc in words
def calc_summand(tf, idf, doc_length, avg_length):
    numerator = tf * (BM25_K1 + 1)
    denominator = tf + BM25_K1 * (1 - BM25_B + BM25_B * (doc_length / avg_length))
    return idf * ((numerator / denominator) + BM25_delta)


# Calculates and returns idf given the number of docs containing a term
# count: num of docs containing the term
# total_docs: num of docs in the corpus
def get_idf(count, total_docs):
    # idf is log(           total num of docs + 1                    )
    #           (----------------------------------------------------)
    #           (        num of docs containing the term             )
    numerator = total_docs + 1
    denominator = count
    idf = math.log10(numerator/denominator)
    return idf

# gets geometric mean of idf1 and idf2
# returns idf1 if idf2 is None
def get_geometric_mean(idf1, idf2, max_idf):
    if idf2 == None:
        return idf1
    else:
        idf2 = normalize_idf(idf2, max_idf)
        return math.sqrt(idf1 * idf2)

# gets normalized idf for idfs in en-idf.txt
# max_idf: max idf in cord-19 corpus
def normalize_idf(idf, max_idf):
    # 13.999 is max idf in en-idf.txt
    return (idf / 14) * max_idf

# Returns a dictionary of the query terms and their idfs
def get_idfs(terms, c, max_idf):
    idfs = {}
    for term in (set(terms)):
        # get idf of the term
        c.execute("select idf, idf2 from terms_idf where term = :term;", {"term": term})
        result = c.fetchone()
        idf1 = result[0] if result else 0
        idf2 = result[1] if result else 0
        # get geometric mean
        idf = get_geometric_mean(idf1, idf2, max_idf)
        idfs[term] = idf
    return idfs
