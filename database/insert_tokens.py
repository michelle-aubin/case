import sqlite3
import time

def main():
    start_time = time.time()
    conn = sqlite3.connect("cord19.db")
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    with open("stopWords.txt", "r", encoding="utf-8") as f_in:
        stop_words = {term.strip() for term in f_in}

    with open("tokens_for_db.txt", "r", encoding="utf-8") as f_in:
        for line in f_in:
            term, doc_id, sent_id, off_st, off_en = line.split("|!|")
            if term not in stop_words:
                values = (term, doc_id, int(sent_id), int(off_st))
                try:
                    c.execute("insert into terms values (?, ?, ?, ?);", values)
                except Exception as e:
                    print(e)
                    print(values)
    conn.commit()
    print("Took %s seconds" % (time.time() - start_time))


main()