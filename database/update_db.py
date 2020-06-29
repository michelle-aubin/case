import sqlite3
import db_tools


# Updates 
def main():
    db_name = input("Enter database filename: ")
    conn = sqlite3.connect(db_name)

    reset = True
    ans = input("Update existing tables? (y/n): ")
    if ans.lower() == "y":
        reset = False

    db_tools.insert_sentences(conn, reset)
    db_tools.insert_stop_words(conn, "stopWords.txt")
    db_tools.insert_doc_lengths(conn)
    db_tools.insert_terms(conn, reset)
    db_tools.insert_entities(conn, reset)