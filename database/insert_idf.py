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
                        idf       float,
                        idf2      float,
                        primary key (term)
                    );
                    """)
    conn.commit()

    other_idfs = {}
    with open("idf-terms-norm.txt", "r", encoding="utf-8") as f_in:
        for line in f_in:
            term, idf = line.split("|!|")
            other_idfs[term] = float(idf)

    c.execute(""" select term, count(distinct doc_id)
            from terms
            group by term
    """)

    for row in c:
        try:
            other_idf = other_idfs[row[0]]
        except KeyError:
            other_idf = None
        finally:
            values = (row[0], get_idf(row[1]), other_idf)
            c2.execute("insert into idf values (?, ?, ?);", values)
    conn.commit()

main()