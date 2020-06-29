import sqlite3
import math
from constants import BM25_B, BM25_K1, BM25_delta


# Returns BM25 score of a document
# doc_id: id of the document
# terms: list of query terms that are not entities
# entities: list of query terms that are entities
# total_docs: num of docs in the corpus
def get_score(doc_id, terms, entities, total_docs, avg_length):
    conn = sqlite3.connect("cord19.db")
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    c.execute("select length from doc_lengths where doc_id = :doc_id;", {"doc_id":doc_id})
    doc_length = c.fetchone()[0]

    score = 0

    for term in terms:
        # get idf of the term
        c.execute("select idf from idf where term = :term;", {"term": term})
        result = c.fetchone()
        idf = result[0] if result else get_idf(0, total_docs)
        # get tf of the term in the doc
        c.execute("select frequency from tf where term = :term and doc_id = :doc_id;", {"term": term, "doc_id":doc_id})
        result = c.fetchone()
        tf = result[0] if result else 0
        # if term is not in doc return score of 0
        if tf == 0:
            return 0
        # calculate score
        score += calc_summand(tf, idf, doc_length, avg_length)
    for ent in entities:
        # get idf of the entity
        c.execute("select idf from ent_idf where entity = :entity;", {"entity": ent})
        result = c.fetchone()
        idf = result[0] if result else get_idf(0, total_docs)
        # get tf of the entity in the doc
        c.execute("select frequency from ent_tf where entity = :entity and doc_id = :doc_id;", {"entity": ent, "doc_id":doc_id})
        result = c.fetchone()
        tf = result[0] if result else 0
        # if term is not in doc return score of 0
        if tf == 0:
            return 0
        # calculate score
        score += calc_summand(tf, idf, doc_length, avg_length)
    
    return score

# Calculates and returns the summand for one query term of bm25 formula
# tf: the term frequency of the term in the doc
# idf: the inverse document frequency of the term
# doc_length: the length of the doc in words
def calc_summand(tf, idf, doc_length, avg_length):
    numerator = tf * (BM25_K1 + 1)
#    print("\t\tNumerator: %f" % numerator)
    denominator = tf + BM25_K1 * (1 - BM25_B + BM25_B * (doc_length / avg_length))
#    print("\t\tDenominator: %f" % denominator)
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

