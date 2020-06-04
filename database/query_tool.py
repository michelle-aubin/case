import sqlite3
import spacy

def main():
    conn = sqlite3.connect("cord19.db")
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    print("Loading model...")
  #  nlp = spacy.load("../custom_model3")
    text = ""

    c.execute("""select count(distinct s.doc_id)
              from entities s
              ;""")
    print(c.fetchall())


    # for row in c:
    #     print(row)
    #     break

    # while text != "quit":
    #     text = input("Enter a question: ")
    #     doc = nlp(text)
    #     print("Entities found:")
    #     for ent in doc.ents:
    #         print("\t%s" % ent.text)
        
    #     for ent in doc.ents:
    #         c.execute("""select DISTINCT s.doc_id, s.sentence 
    #                     from sentences s, entities e 
    #                     where s.doc_id = e.doc_id and s.sent_id = e.sent_id
    #                     and e.entity = :ent;  """, {"ent":ent.text})
    #         conn.commit()
    #         sents = c.fetchall()
    #         for sent in sents:
    #             print(sent)

main()