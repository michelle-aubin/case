import sqlite3
import spacy
from bm25 import get_score
import csv

def main():
    conn = sqlite3.connect("cord19.db")
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    stop_words = set()
    # with open("stopWords.txt", "r") as f_stop:
    #     for line in f_stop:
    #         stop_words.add(line.strip())
    c.execute("select term from stop_words;")
    for row in c:
        stop_words.add(row[0])

    print("Loading model...")
    nlp = spacy.load("../custom_model3")
    text = ""

    while text != "quit":
        terms = []
        entities = []
        text = input("Enter a question: ")
        doc = nlp(text)
        print("Entities found:")
        for ent in doc.ents:
            print("\t%s" % ent.text)
            entities.append(ent.text)

        print("Tokens found:")
        for token in doc:
          # if token is a non entity and not a punct and not a stop word
          if token.ent_iob == 2 and not token.is_punct and token.text not in stop_words:
            print("\t%s" % token.text)
            terms.append(token.text)

        # terms = ["antiviral", "treatment"]

        # get docs that have all of the entities and tokens? or that have at least one? or just do all docs?
        doc_scores = {}
        with open("doc_ids.txt", "r", encoding="utf-8") as f_docs:
            for row in f_docs:
                doc_id = row.strip()
                doc_scores[doc_id] = get_score(doc_id, terms, entities)
        i = 0
        for doc, score in sorted(doc_scores.items(), key=lambda item: item[1], reverse=True):
            if i > 10:
                break
            i += 1
            print(doc, score)



main()