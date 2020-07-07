import plac
import sqlite3
import spacy
from query_tool import get_queries, get_terms_and_ents

# Returns a dictionary of doc_ids that have a relevance score of 1 or 2 (partially or fully relevant)
# Given a topic number, t
def get_judgements(input_file, t):
    judgements = {}
    with open(input_file, "r") as f_in:
        for line in f_in:
            tnum, iteration, doc_id, score = line.split()
            tnum = int(tnum)
            if tnum < t:
                continue
            elif tnum > t:
                return judgements
            else:
                judgements[doc_id] = int(score.strip())
    return judgements

@plac.annotations(
    f_key=("File name of the TREC-COVID relevance judgement set.", "positional", None, str),
    f_queries=("File name of the query set.", "positional", None, str),
    tnum=("Topic number to look at", "positional", None, int),
    db_name=("Database name", "positional", None, str)
)
def main(f_key, f_queries, tnum, db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    nlp = spacy.load("../custom_model3")

    # get stop words
    stop_words = set()
    c.execute("select word from stop_words;")
    for row in c:
        stop_words.add(row[0])

    docs = get_judgements(f_key, tnum)
    query = get_queries(f_queries)[tnum-1]
    terms, entities, splitted_terms, splitted_ents = get_terms_and_ents(query, nlp, stop_words)

    print("doc id  ", end="")
    for term in terms:
        print("\t%s" % term, end="")
    for ent in entities:
        print("\t%s" % ent, end="")
    print()


    for doc_id in docs:
        print(doc_id, end="")
        for term in terms:
            # get tf of the term in the doc
            c.execute("select frequency from terms_tf where term = :term and doc_id = :doc_id;", {"term": term, "doc_id":doc_id})
            result = c.fetchone()
            tf = result[0] if result else 0
            print("\t%.3f" % tf, end="")

        for ent in entities:
            # get tf of the entity in the doc
            c.execute("select frequency from ents_tf where entity = :entity and doc_id = :doc_id;", {"entity": ent, "doc_id":doc_id})
            result = c.fetchone()
            tf = result[0] if result else 0
            print("\t%.3f" % tf, end="")
        print()
    
    

if __name__ == "__main__":
    plac.call(main)