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
                        idf       double,
                        primary key (entity)
                    );
                    """)
    conn.commit()

    c.execute(""" select entity, count(distinct doc_id)
                from entities
                group by entity
        """)

    for row in c:
        values = (row[0], get_idf(row[1]))
        c2.execute("insert into ent_idf values (?, ?);", values)
    conn.commit()
main()

