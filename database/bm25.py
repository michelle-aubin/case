import sqlite3
import math
from constants import BM25_B, BM25_K1, BM25_delta, TF_F0


# Returns BM25 score of a document
# doc_id: id of the document
# terms: list of query terms that are not entities
# entities: list of query terms that are entities
# total_docs: num of docs in the corpus
def get_score(doc_id, terms, entities, total_docs, avg_length, max_idf):
    conn = sqlite3.connect("cord19.db")
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    c.execute("select length from doc_lengths where doc_id = :doc_id;", {"doc_id":doc_id})
    doc_length = c.fetchone()[0]
    default_tf = get_tf(0, doc_length, get_num_unique(doc_id, c))

    score = 0

    for term in terms:
        # get idf of the term
        c.execute("select idf, idf2 from terms_idf where term = :term;", {"term": term})
        result = c.fetchone()
        idf1 = result[0] if result else 0
        idf2 = result[1] if result else 0
        # get geometric mean
        idf = get_geometric_mean(idf1, idf2, max_idf)
        # get tf of the term in the doc
        c.execute("select frequency from terms_tf where term = :term and doc_id = :doc_id;", {"term": term, "doc_id":doc_id})
        result = c.fetchone()
        tf = result[0] if result else default_tf
        # if term is not in doc return score of 0
        # if tf == 0:
        #     return 0
        # calculate score
        score += calc_summand(tf, idf, doc_length, avg_length)
    for ent in entities:
        # get idf of the entity
        c.execute("select idf, idf2 from ents_idf where entity = :entity;", {"entity": ent})
        result = c.fetchone()
        idf1 = result[0] if result else 0
        idf2 = result[1] if result else 0
        # get geometric mean
        idf = get_geometric_mean(idf1, idf2, max_idf)
        # get tf of the entity in the doc
        c.execute("select frequency from ents_tf where entity = :entity and doc_id = :doc_id;", {"entity": ent, "doc_id":doc_id})
        result = c.fetchone()
        tf = result[0] if result else default_tf
        # if term is not in doc return score of 0
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

# Calculates and returns tf given the raw count of a term in a doc,
# the doc length and num of unique terms in the doc
# count: num of times that the term appears in the doc
# doc_length: length of the doc in words
# num_unique: num of unique terms in the doc
def get_tf(count, doc_length, num_unique):
    numerator = count + TF_F0
    denominator = doc_length + (TF_F0 * num_unique)
    return numerator / denominator

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

# Returns the number of unique terms + unique entities in a doc
# doc_id: the document id
# c: cursor for the database
def get_num_unique(doc_id, c):
    c.execute("select count(distinct term) from terms where doc_id = :doc_id;", {"doc_id": doc_id})
    num_unique = c.fetchone()[0]
    c.execute("select count(distinct entity) from entities where doc_id = :doc_id;", {"doc_id": doc_id})
    num_unique += c.fetchone()[0]
    return num_unique

def get_num_unique_dict(c):
    c.execute(""" select count(distinct term), doc_id
                    from terms
                    group by doc_id;
            """)
    nu_dict = {}
    for row in c:
        nu_dict[row[1]] = row[0]

    c.execute(""" select count(distinct entity), doc_id
                    from entities
                    group by doc_id;
            """)   
    for row in c:
        try:
            nu_dict[row[1]] += row[0]
        except KeyError:
            nu_dict[row[1]] = row[0]
    return nu_dict