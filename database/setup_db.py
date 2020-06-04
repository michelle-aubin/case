import sqlite3

def main():
    conn = sqlite3.connect("cord19.db")
    c = conn.cursor()

    c.executescript("""
                    drop table if exists sentences;
                    drop table if exists entities;
                    drop table if exists stop_words;
                    """)

    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    c.executescript("""
                    create table sentences (
                        doc_id      char(8),
                        sent_id     int,
                        sentence    text,
                        primary key (doc_id,sent_id)        
                    );
                    create table entities (
                        entity      text,
                        type        char(35),
                        doc_id      char(8),
                        sent_id     int,
                        start       int,
                        end         int,
                        primary key (doc_id,sent_id,start),
                        foreign key (doc_id,sent_id) references sentences
                    );
                    create table stop_words (
                            term      text,
                            primary key (term)        
                        );
                    """)
    conn.commit()


main()