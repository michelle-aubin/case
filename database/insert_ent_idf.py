import sqlite3
from bm25 import get_idf

# ent_idf(entity, idf)
def main():
    conn = sqlite3.connect("cord19.db")
    c = conn.cursor()
    c2 = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    c.executescript("""
                    drop table if exists ent_idf;
                    create table ent_idf (
                        entity      text,
                        idf       float,
                        idf2      float,
                        primary key (entity)
                    );
                    """)
    conn.commit()

    other_idfs = {}
    with open("idf-ents-norm.txt", "r", encoding="utf-8") as f_in:
        for line in f_in:
            ent, idf = line.split("|!|")
            other_idfs[ent] = float(idf)

    c.execute(""" select entity, count(distinct doc_id)
                from entities
                group by entity
        """)

    for row in c:
        try:
            other_idf = other_idfs[row[0]]
        except KeyError:
            other_idf = None
        finally:
            values = (row[0], get_idf(row[1]), other_idf)
            c2.execute("insert into ent_idf values (?, ?, ?);", values)
    conn.commit()
main()

