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
                        frequency   float,
                        primary key (entity, doc_id)
                    );
                    """)
    conn.commit()

    start = time.time()
    c.execute(""" select e.entity, e.doc_id, count(*), d.length
                    from entities e, doc_lengths d
                    where e.doc_id = d.doc_id
                    group by e.entity, e.doc_id;
            """)
    print("Querying db took %s seconds", time.time() - start)
    for row in c:
        values = (row[0], row[1], row[2] / row[3])
        c2.execute("insert into ent_tf values (?, ?, ?);", values)
    conn.commit()
main()