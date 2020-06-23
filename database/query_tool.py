import sqlite3
import spacy
from bm25 import get_score, print_get_score
import time
from constants import URL
import csv
import plac
from xml.dom import minidom

# Returns a dictionary with doc ids as key and score of 0 as values
def get_doc_ids():
    doc_scores = {}
    # all docs
    with open("doc_ids.txt", "r", encoding="utf-8") as f_docs:
        for row in f_docs:
            doc_id = row.strip()
            doc_scores[doc_id] = 0

    # only docs that are related to covid19
    # c.execute("select distinct doc_id from entities where type = \"CORONAVIRUS\";")
    # for row in c:
    #     doc_id = row[0]
    #     doc_scores[doc_id] = 0

    return doc_scores


@plac.annotations(
   input_file=("Input text file of queries", "positional", None, str),
   output_file=("Output file", "positional", None, str), 
)
def main(input_file, output_file):
    conn = sqlite3.connect("cord19.db")
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    stop_words = set()
    c.execute("select term from stop_words;")
    for row in c:
        stop_words.add(row[0])

    # get links to json files of the docs
    # urls = {}
    # with open("../clean_metadata.csv", "r", encoding="utf-8") as f_meta:
    #     metadata = csv.DictReader(f_meta)
    #     for row in metadata:
    #         urls[row.get("cord_uid")] = row.get("json_file")

    print("Loading model...")
    nlp = spacy.load("../custom_model3")

    doc_scores = get_doc_ids()

    with open(input_file, "r") as f_in:
        for line in f_in:
            terms = []
            entities = []
            doc = nlp(line.strip())
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
                doc_scores[doc_id] = get_score(doc_id, terms, entities)

            print("Took %.2f seconds to get scores" % (time.time() - start))
            i = 0
            with open(output_file, "a") as f_out:
                for doc, score in sorted(doc_scores.items(), key=lambda item: item[1], reverse=True):
                    if i >= 5:
                        f_out.write("\n")
                        break
                    i += 1
                    f_out.write(doc + "\n")

if __name__ == "__main__":
    start_time = time.time()
    plac.call(main)
    print("-- %s seconds --" % (time.time() - start_time))