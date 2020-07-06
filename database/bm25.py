import sqlite3
import math
from constants import BM25_B, BM25_K1, BM25_delta


# Returns BM25 score of a document
# doc_id: id of the document
# terms: list of query terms that are not entities
# entities: list of query terms that are entities
# total_docs: num of docs in the corpus
# idfs: dictionary of terms and idf values
# c: database cursor
def get_score(doc_id, terms, entities, total_docs, avg_length, idfs, c):
    c.execute("select length from doc_lengths where doc_id = :doc_id;", {"doc_id":doc_id})
    doc_length = c.fetchone()[0]
    # remove docs that are smaller than 25 words
    if doc_length < 25:
        return 0
    score = 0
    for term in terms:
        idf = idfs[term]
        # get tf of the term in the doc
        c.execute("select frequency from terms_tf where term = :term and doc_id = :doc_id;", {"term": term, "doc_id":doc_id})
        result = c.fetchone()
        tf = result[0] if result else 0
        # # if term is not in doc return score of 0
        # if tf == 0:
        #     return 0
        # calculate score
        score += calc_summand(tf, idf, doc_length, avg_length)
    for ent in entities:
        idf = idfs[ent]
        # get tf of the entity in the doc
        c.execute("select frequency from ents_tf where entity = :entity and doc_id = :doc_id;", {"entity": ent, "doc_id":doc_id})
        result = c.fetchone()
        tf = result[0] if result else 0
        # # if term is not in doc return score of 0
        # if tf == 0:
        #     return 0
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
def get_idfs(terms, entities, splitted_terms, splitted_ents, c, max_idf):
    idfs = {}
    for term1, term2 in zip(terms, splitted_terms):
        # get idf of the term
        c.execute("select idf, idf2 from terms_idf where term = :term;", {"term": term1})
        result = c.fetchone()
        idf1 = result[0] if result else 0
        idf2 = result[1] if result else 0
        # get geometric mean
        idf = get_geometric_mean(idf1, idf2, max_idf)
        idfs[term1] = idf
        # has splitted
        if term1 != term2:
            c.execute("select idf, idf2 from terms_idf where term = :term;", {"term": term2})
            result = c.fetchone()
            idf1 = result[0] if result else 0
            idf2 = result[1] if result else 0
            # get geometric mean
            idf = get_geometric_mean(idf1, idf2, max_idf)
            idfs[term2] = idf
    for ent1, ent2 in zip(entities, splitted_ents):
        # get idf of the entity
        c.execute("select idf, idf2 from ents_idf where entity = :entity;", {"entity": ent1})
        result = c.fetchone()
        idf1 = result[0] if result else 0
        idf2 = result[1] if result else 0
        # get geometric mean
        idf = get_geometric_mean(idf1, idf2, max_idf)
        idfs[ent1] = idf
        # has splitted
        if ent1 != ent2:
            # get idf of the entity
            c.execute("select idf, idf2 from ents_idf where entity = :entity;", {"entity": ent2})
            result = c.fetchone()
            idf1 = result[0] if result else 0
            idf2 = result[1] if result else 0
            # get geometric mean
            idf = get_geometric_mean(idf1, idf2, max_idf)
            idfs[ent2] = idf
    return idfs
