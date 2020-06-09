import sqlite3
import time

# tf (term, docId, tf)
def main():
    conn = sqlite3.connect("cord19.db")
    c = conn.cursor()
    c2 = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    c.executescript("""
                    drop table if exists tf;""")
    c.executescript("""
                    create table tf (
                        term        text,
                        doc_id      char(8),
                        frequency   int,
                        primary key (term, doc_id)
                    );
                    """)
    conn.commit()

    start = time.time()
    c.execute(""" select t.term, t.doc_id, count(*), d.length
                    from terms t, doc_lengths d
                    where t.doc_id = d.doc_id
                    group by t.term, t.doc_id;
            """)
    print("Querying db took %s seconds", time.time() - start)
    for row in c:
        values = (row[0], row[1], row[2] / row[3])
        c2.execute("insert into tf values (?, ?, ?);", values)
    conn.commit()
main()