import sqlite3

def main():
    conn = sqlite3.connect("cord19.db")
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")

    c.executescript("""
                    drop table if exists terms;
                    """)

    c.executescript("""
                    create table terms (
                        term      text,
                        doc_id      char(8),
                        sent_id     int,
                        start       int,
                        primary key (doc_id,sent_id,start),
                        foreign key (doc_id,sent_id) references sentences
                    );
                    """)
    conn.commit()

    with open("stopWords.txt", "r", encoding="utf-8") as f_in:
        stop_words = {term.strip() for term in f_in}

    with open("tokens_for_db.txt", "r", encoding="utf-8") as f_in:
        for line in f_in:
            term, doc_id, sent_id, off_st, off_en = line.split("|!|")
            if term not in stop_words:
                values = (term, doc_id, int(sent_id), int(off_st))
                c.execute("insert into terms values (?, ?, ?, ?);", values)
    conn.commit()


main()