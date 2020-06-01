import spacy
import sqlite3

def main():
    conn = sqlite3.connect("cord19.db")
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    print("Loading model...")
    nlp = spacy.load("../custom_model3")

    with open("non_entities.txt", "w", encoding="utf-8") as f_out:
        c.execute("SELECT * FROM sentences;")
        for row in c:
            doc_id = row[0]
            sent_id = row[1]
            text = row[2]
            doc = nlp(text)
            for token in doc:
                # only take non entities and non punctuation
                # and take lowercase form
                if token.ent_iob == 2 and not token.is_punct:
                    output = token.lower_ + "|" + doc_id + "|" + str(sent_id) + "\n"
                    f_out.write(output)
    

main()