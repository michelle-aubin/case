import sqlite3
import time
import os
from constants import SEP

def main():
    start_time = time.time()
    conn = sqlite3.connect("cord19.db")
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    c.executescript("""
                    drop table if exists terms;
                    create table terms (
                        term        text,
                        doc_id      char(8),
                        sent_id     int,
                        start       int,
                        primary key (doc_id,sent_id,start),
                        foreign key (doc_id,sent_id) references sentences
                    );
                    """)

    with open("stopWords.txt", "r", encoding="utf-8") as f_in:
        stop_words = {term.strip() for term in f_in}

    for root, dirs, files in os.walk("../terms"):
        for name in files:
            data = []
            fpath = os.path.join(root, name)
            with open(fpath, "r", encoding="utf-8") as f_in:
                for line in f_in:
                    entry = line.split(SEP)
                    try:
                        if entry[0].lower() not in stop_words:
                            values = (entry[0].lower(), entry[1], int(entry[2]), int(entry[3]))
                            c.execute("insert into terms values (?, ?, ?, ?);", values)
                    except Exception as e:
                        print(e)
                        print("Bad line: ", entry)

    conn.commit()
    print("Took %s seconds" % (time.time() - start_time))


main()