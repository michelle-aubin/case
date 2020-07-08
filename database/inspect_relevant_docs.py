import plac
import sqlite3
import spacy
from query_tool import get_terms_and_ents
from xml.dom import minidom

# Returns a list of queries
def get_queries(input_file):
    queries = []
    xml_doc = minidom.parse(input_file)
    topics = xml_doc.getElementsByTagName('topic')
    for topic in topics:
        query = topic.getElementsByTagName('query')[0].childNodes[0].data
        # question = topic.getElementsByTagName('question')[0].childNodes[0].data
        # narrative = topic.getElementsByTagName('narrative')[0].childNodes[0].data
        # full = ". ".join([query, question, narrative])
        queries.append(query)
    return queries

# Returns a dictionary of doc_ids that have a relevance score of 1 or 2 (partially or fully relevant)
# Given a topic number, t
def get_judgements(input_file, t):
    judgements = {}
    with open(input_file, "r") as f_in:
        for line in f_in:
            tnum, iteration, doc_id, score = line.split()
            tnum = int(tnum)
            # if tnum < t:
            #     continue
            # elif tnum > t:
            #     return judgements
            # else:
            score = int(score.strip())
            if score > 0:
                judgements[doc_id] = score
    return judgements

@plac.annotations(
    f_key=("File name of the TREC-COVID relevance judgement set.", "positional", None, str),
    f_queries=("File name of the query set.", "positional", None, str),
    db_name=("Database name", "positional", None, str)
)
def main(f_key, f_queries, db_name):
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

    for tnum in range(1,41):
        docs = get_judgements(f_key, tnum)
        query = get_queries(f_queries)[tnum-1]
        terms, entities, splitted_terms, splitted_ents = get_terms_and_ents(query, nlp, stop_words)

        # print("doc id  ", end="")
        # for term in terms:
        #     print("\t%s" % term, end="")
        # for ent in entities:
        #     print("\t%s" % ent, end="")
        # print()

        counts = { "contains 0 terms": 0, "contains some terms": 0, "contains all terms": 0}

        for doc_id in docs:
            # print(doc_id, end="")
            num_terms = set()
            for term in terms:
                # get tf of the term in the doc
                c.execute("select frequency from terms_tf where term = :term and doc_id = :doc_id;", {"term": term, "doc_id":doc_id})
                result = c.fetchone()
                tf = result[0] if result else 0
                num_terms.add(tf)
                # print("\t%.3f" % tf, end="")

            for ent in entities:
                # get tf of the entity in the doc
                c.execute("select frequency from ents_tf where entity = :entity and doc_id = :doc_id;", {"entity": ent, "doc_id":doc_id})
                result = c.fetchone()
                tf = result[0] if result else 0
                num_terms.add(tf)
                
                # print("\t%.3f" % tf, end="")
            # print()
            if len(num_terms) == 1 and 0 in num_terms:
                counts["contains 0 terms"] += 1
            elif 0 not in num_terms:
                counts["contains all terms"] += 1
            else:
                counts["contains some terms"] += 1

        with open("count_for_rel_docs.txt", "a") as f_out:
            f_out.write("Topic %d: %s\n" % (tnum, query))
            for key, value in counts.items():
                f_out.write("\t%s: %d\n" % (key, value))
    
    

if __name__ == "__main__":
    plac.call(main)