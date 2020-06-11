import sqlite3
import math
from constants import AVG_DOC_LENGTH, BM25_B, BM25_K1, TOTAL_DOCS, BM25_delta


# Returns BM25 score of a document
# doc_id: id of the document
# terms: list of query terms that are not entities
# entities: list of query terms that are entities
def get_score(doc_id, terms, entities):
    conn = sqlite3.connect("cord19.db")
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    c.execute("select length from doc_lengths where doc_id = :doc_id;", {"doc_id":doc_id})
    doc_length = c.fetchone()[0]
    print("For Doc %s:" % doc_id)
    print("\tLength: %d" % doc_length)

    score = 0
    print("\tScore: %f" % score)
    for term in terms:
        print("\tFor term \"%s\":" % term)
        # get idf of the term
        c.execute("select idf from idf where term = :term;", {"term": term})
        result = c.fetchone()
        idf = result[0] if result else get_idf(0)
        print("\t\tIDF: %f" % idf)
        # get tf of the term in the doc
        c.execute("select frequency from tf where term = :term and doc_id = :doc_id;", {"term": term, "doc_id":doc_id})
        result = c.fetchone()
        tf = result[0] if result else 0
        print("\t\tTF: %f" % tf)
        # calculate score
        score += calc_summand(tf, idf, doc_length)
        print("\tScore: %f" % score)
    for ent in entities:
        print("\tFor entity \"%s\":" % ent)
        # get idf of the entity
        c.execute("select idf from ent_idf where entity = :entity;", {"entity": ent})
        result = c.fetchone()
        idf = result[0] if result else get_idf(0)
        print("\t\tIDF: %f" % idf)
        # get tf of the entity in the doc
        c.execute("select frequency from ent_tf where entity = :entity and doc_id = :doc_id;", {"entity": ent, "doc_id":doc_id})
        result = c.fetchone()
        tf = result[0] if result else 0
        print("\t\tTF: %f" % tf)
        # calculate score
        score += calc_summand(tf, idf, doc_length)
    
    return score

# Calculates and returns the summand for one query term of bm25 formula
# tf: the term frequency of the term in the doc
# idf: the inverse document frequency of the term
# doc_length: the length of the doc in words
def calc_summand(tf, idf, doc_length):
    numerator = tf * (BM25_K1 + 1)
    print("\t\tNumerator: %f" % numerator)
    denominator = tf + BM25_K1 * (1 - BM25_B + BM25_B * (doc_length / AVG_DOC_LENGTH))
    print("\t\tDenominator: %f" % denominator)
    return idf * ((numerator / denominator) + BM25_delta)


# Calculates and returns idf given the number of docs containing a term
# count: num of docs containing the term
def get_idf(count):
    # idf is log(           total num of docs + 1                    )
    #           (----------------------------------------------------)
    #           (        num of docs containing the term             )
    top = TOTAL_DOCS + 1
    bottom = count
    idf = math.log(top/bottom)
    return idf