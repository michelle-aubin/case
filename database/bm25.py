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

# Returns a dictionary of the query terms and their idfs
def get_idfs(terms, c):
    idfs = {}
    for term in (terms):
        # get idf of the term
        c.execute("select idf from idf where term = :term;", {"term": term})
        result = c.fetchone()
        idf = result[0] if result else 0
        idfs[term] = idf
    return idfs
