import sqlite3
from constants import AVG_DOC_LENGTH, BM25_B, BM25_K1


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

    score = 0
    for term in terms:
        c.execute("select idf from idf where term = :term;", {"term": term})
        idf = c.fetchone()[0]
        c.execute("select frequency from tf where term = :term and doc_id = :doc_id;", {"term": term, "doc_id":doc_id})
        tf = c.fetchone()[0]
        top = tf * (BM25_K1 + 1)
        bottom = tf + BM25_K1 * (1 - BM25_B + BM25_B * (doc_length / AVG_DOC_LENGTH))
        score += idf * (top / bottom)
    return score


