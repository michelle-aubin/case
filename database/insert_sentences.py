import sqlite3
import os
import time
from constants import SEP

def main():
    conn = sqlite3.connect("cord19.db")
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    c.executescript("""
                    drop table if exists sentences;
                    create table sentences (
                        doc_id      char(8),
                        sent_id     int,
                        sentence    text,
                        primary key (doc_id,sent_id)        
                    );
                    """)
    conn.commit()

    # iterate through files in sentences directory
    for root, dirs, files in os.walk("..\sentences"):
        for name in files:
            data = []
            fpath = os.path.join(root, name)
            print(fpath)
            with open(fpath, "r", encoding="utf-8") as f_in:
                for line in f_in:
                    entry = line.split(SEP)
                    try:
                        values = (entry[0], int(entry[1]), entry[2].strip('\n'))
                        c.execute("insert into sentences values (?, ?, ?);", values)
                    except Exception as e:
                        print(e)
                        print("Bad line: ", entry)
        com_time = time.time()
        conn.commit()
        print("Committing took %s seconds" % (time.time() - com_time))


main()
    