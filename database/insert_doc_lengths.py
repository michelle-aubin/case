import sqlite3
from collections import defaultdict

# gets total number of words for each doc
def main():
    doc_lengths = defaultdict(lambda: 0)
    conn = sqlite3.connect("cord19.db")
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    # get all sentences for docs
    c.execute(""" select sentence, doc_id
                    from sentences
                """)
    
    # count words by splitting on spaces
    for row in c:
        sentence = row[0].split()
        doc_id = row[1]
        doc_lengths[doc_id] += len(sentence)

    c.executescript("""
                    drop table if exists doc_lengths;""")
    c.executescript("""
                    create table doc_lengths (
                        doc_id      char(8),
                        length   int,
                        primary key (doc_id)
                    );
                    """)
    conn.commit()

    for doc_id, length in doc_lengths.items():
        if length != 0:
            c.execute("insert into doc_lengths values (?, ?);", (doc_id, length))
    conn.commit()

main()