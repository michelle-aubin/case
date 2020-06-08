import sqlite3
import time

# ent_tf (entity, docId, tf)
def main():
    conn = sqlite3.connect("cord19.db")
    c = conn.cursor()
    c2 = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    c.executescript("""
                    drop table if exists ent_tf;""")
    c.executescript("""
                    create table ent_tf (
                        entity        text,
                        doc_id      char(8),
                        frequency   int,
                        primary key (entity, doc_id)
                    );
                    """)
    conn.commit()

    start = time.time()
    c.execute(""" select entity, doc_id, count(*)
                    from entities
                    group by entity, doc_id
            """)
    print("Querying db took %s seconds", time.time() - start)
    for row in c:
        values = (row[0], row[1], row[2])
        c2.execute("insert into ent_tf values (?, ?, ?);", values)
    conn.commit()
main()