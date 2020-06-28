import sqlite3

def main():
    conn = sqlite3.connect("cord19.db")
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    c.executescript("""
                    drop table if exists stop_words;
                    create table stop_words (
                        word      text,
                        primary key (word)        
                    );
                    """)


    with open("stopWords.txt", "r", encoding="utf-8") as f_in:
        for term in f_in:
            term = term.strip()
            c.execute("insert into stop_words values (?);", (term,))
    conn.commit()

main()
