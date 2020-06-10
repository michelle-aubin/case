import sqlite3
import spacy
from bm25 import get_score
import time
from constants import URL
import csv

def main():
    conn = sqlite3.connect("cord19.db")
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    stop_words = set()
    c.execute("select term from stop_words;")
    for row in c:
        stop_words.add(row[0])

    # get links to json files of the docs
    urls = {}
    with open("../clean_metadata.csv", "r", encoding="utf-8") as f_meta:
        metadata = csv.DictReader(f_meta)
        for row in metadata:
            urls[row.get("cord_uid")] = row.get("json_file")

    print("Loading model...")
    nlp = spacy.load("../custom_model3")
    text = ""

    text = input("Enter a question: ")
    while text != "quit":
        terms = []
        entities = []
        doc = nlp(text)
        print("Entities found:")
        for ent in doc.ents:
            print("\t%s" % ent.text)
            entities.append(ent.text.lower())

        print("Tokens found:")
        for token in doc:
          # if token is a non entity and not a punct and not a stop word
          if token.ent_iob == 2 and not token.is_punct and token.text.lower() not in stop_words:
            print("\t%s" % token.text)
            terms.append(token.text.lower())
        # terms = ["antiviral", "treatment"]

        print("Getting scores...")
        start = time.time()
        # get docs that have all of the entities and tokens? or that have at least one? or just do all docs?
        doc_scores = {}
        with open("doc_ids.txt", "r", encoding="utf-8") as f_docs:
            for row in f_docs:
                doc_id = row.strip()
                doc_scores[doc_id] = get_score(doc_id, terms, entities)
        print("Took %.2f seconds to get scores" % (time.time() - start))
        i = 0
        for doc, score in sorted(doc_scores.items(), key=lambda item: item[1], reverse=True):
            if i > 5:
                break
            i += 1
            print("Doc ID: %s       Score: %.4f     Link: %s" % (doc, score, URL + urls[doc]))
        # print("Scores of top docs from kaggle engine:")
        # print("sasijnks", doc_scores["sasijnks"])
        # print("sasijnks", doc_scores["itz0bdrc"])
        text = input("Enter a question: ")




main()