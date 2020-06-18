import sqlite3
from bm25 import get_idf

def main():
    conn = sqlite3.connect("cord19.db")
    c = conn.cursor()
    c2 = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    c.executescript("""
                    drop table if exists idf;
                    create table idf (
                        term      text,
                        idf       double,
                        primary key (term)
                    );
                    """)
    conn.commit()

    c.execute(""" select term, count(distinct doc_id)
            from terms
            group by term
    """)

    for row in c:
        values = (row[0], get_idf(row[1]))
        c2.execute("insert into idf values (?, ?);", values)
    conn.commit()

main()