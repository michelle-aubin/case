import sqlite3

def main():
    conn = sqlite3.connect("cord19.db")
    c = conn.cursor()

    c.executescript("""
                    drop table if exists sentences;
                    drop table if exists entities;
                    drop table if exists stop_words;
                    drop table if exists terms;
                    drop table if exists idf;
                    drop table if exists doc_lengths;
                    drop table if exists ent_idf;
                    drop table if exists ent_tf;
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
                    create table terms (
                        term      text,
                        doc_id      char(8),
                        sent_id     int,
                        start       int,
                        primary key (doc_id,sent_id,start),
                        foreign key (doc_id,sent_id) references sentences
                    );
                    create table idf (
                        term      text,
                        idf       double,
                        primary key (term)
                    );
                    create table doc_lengths (
                        doc_id      char(8),
                        length   int,
                        primary key (doc_id)
                    );
                    create table ent_idf (
                        entity      text,
                        idf       double,
                        primary key (entity)
                    );
                    create table ent_tf (
                        entity        text,
                        doc_id      char(8),
                        frequency   int,
                        primary key (entity, doc_id)
                    );
                    """)
    conn.commit()


main()