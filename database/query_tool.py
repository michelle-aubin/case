import sqlite3
import spacy
from bm25 import get_score, get_idf
import time
from constants import URL
# import csv
import plac
from xml.dom import minidom

# Returns a dictionary with doc ids as key and score of 0 as values
# c: cursor for database
def get_doc_ids(c):
    with open("trec-covid/round3/docids-rnd3.txt", "r") as f_in:
        rnd3_docs = {line.strip() for line in f_in}
    doc_scores = {}
    # all docs
    c.execute("select doc_id from doc_lengths;")
    for row in c:
        doc_id = row[0]
        if doc_id in rnd3_docs:
            doc_scores[doc_id] = 0

    # only docs that are related to covid19
    # c.execute("select distinct doc_id from entities where type = \"CORONAVIRUS\";")
    # for row in c:
    #     doc_id = row[0]
    #     doc_scores[doc_id] = 0

    return doc_scores

# Returns a list of queries
def get_queries(input_file):
    queries = []
    xml_doc = minidom.parse(input_file)
    topics = xml_doc.getElementsByTagName('topic')
    for topic in topics:
        queries.append(topic.getElementsByTagName('question')[0].childNodes[0].data)
    return queries


@plac.annotations(
   input_file=("Input text file of queries", "positional", None, str),
   output_file=("Output file", "positional", None, str), 
   run_tag=("Tag representing the run", "positional", None, str)
)
def main(input_file, output_file, run_tag):
    conn = sqlite3.connect("cord19.db")
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    print("Gathering some data...")
    stop_words = set()
    c.execute("select word from stop_words;")
    for row in c:
        stop_words.add(row[0])

    # get links to json files of the docs
    # urls = {}
    # with open("../clean_metadata.csv", "r", encoding="utf-8") as f_meta:
    #     metadata = csv.DictReader(f_meta)
    #     for row in metadata:
    #         urls[row.get("cord_uid")] = row.get("json_file")

    doc_scores = get_doc_ids(c)
    queries = get_queries(input_file)
    
    c.execute("select count(doc_id) from doc_lengths;")
    total_docs = c.fetchone()[0]

    avg_length = 0
    for doc in doc_scores:
        c.execute("select length from doc_lengths where doc_id = :doc_id", {"doc_id": doc})
        length = c.fetchone()[0]
        avg_length += length
    avg_length = avg_length / total_docs

    max_idf = get_idf(1, total_docs)

    print("Loading model...")
    nlp = spacy.load("../custom_model3")

    for tnum, query in enumerate(queries):
        terms = []
        entities = []
        tnum += 1
        doc = nlp(query)
        print("Entities found:")
        for ent in doc.ents:
            print("\t%s" % ent.text)
            entities.append(ent.text.lower())

        print("Terms found:")
        for token in doc:
            # if token is a non entity and not a punct and not a stop word
            if token.ent_iob == 2 and not token.is_punct and token.text.lower() not in stop_words:
                print("\t%s" % token.text)
                terms.append(token.text.lower())


        print("Getting scores...")
        start = time.time()
        for doc_id in doc_scores:
            doc_scores[doc_id] = get_score(doc_id, terms, entities, total_docs, avg_length, max_idf)

        print("Took %.2f seconds to get scores" % (time.time() - start))
        i = 0
        with open(output_file, "a") as f_out:
            for doc, score in sorted(doc_scores.items(), key=lambda item: item[1], reverse=True):
                # return max 1000 docs
                if i >= 1000 or score == 0:
                    # no docs returned
                    if i == 0:
                        # make dummy list
                        output_vals = [str(tnum), "Q0", doc, str(j+1), str(score), run_tag, "\n"]
                        f_out.write("\t".join(output_vals))
                    break
                i += 1
                output_vals = [str(tnum), "Q0", doc, str(i), str(score), run_tag, "\n"]
                f_out.write("\t".join(output_vals))

if __name__ == "__main__":
    start_time = time.time()
    plac.call(main)
    print("-- %s seconds --" % (time.time() - start_time))