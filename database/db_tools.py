import sqlite3
import os
import time
from constants import SEP
from collections import defaultdict
from bm25 import get_idf

# Inserts values into entities table
# conn: connection to the database
# reset: a bool, if True drops old table and creates new one 
def insert_entities(conn, reset):
    start = time.time()
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    
    if reset:
        c.executescript("""
                    drop table if exists entities;
                    create table entities (
                                        entity      text,
                                        type        char(35),
                                        doc_id      char(8),
                                        sent_id     int,
                                        start       int,
                                        primary key (doc_id,sent_id,start),
                                        foreign key (doc_id,sent_id) references sentences
                                    );
                    """)
    for root, dirs, files in os.walk("..\entities"):
        for name in files:
            data = []
            fpath = os.path.join(root, name)
            with open(fpath, "r", encoding="utf-8") as f_in:
                for line in f_in:
                    entry = line.split(SEP)
                   # print(entry)
                    try:
                        # entity|type|doc_id|sent_id|start|end
                        values = (entry[0].lower(), entry[1], entry[2], int(entry[3]), int(entry[4]))
                        c.execute("insert into entities values (?, ?, ?, ?, ?);", values)
                    except Exception as e:
                        print(e)
                        print("Bad line: ", entry)
    conn.commit()
    print("Populating entities took %s seconds" % (time.time() - start))
    insert_ents_idf(conn)
    insert_ents_tf(conn)

# Inserts values into terms table
# conn: connection to the database
# reset: a bool, if True drops old table and creates new one 
def insert_terms(conn, reset):
    start = time.time()
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    if reset:
        c.executescript("""
                        drop table if exists terms;
                        create table terms (
                            term        text,
                            doc_id      char(8),
                            sent_id     int,
                            start       int,
                            primary key (doc_id,sent_id,start),
                            foreign key (doc_id,sent_id) references sentences
                        );
                        """)

    c.execute("select word from stop_words;")
    stop_words = {row[0] for row in c}

    for root, dirs, files in os.walk("../terms"):
        for name in files:
            data = []
            fpath = os.path.join(root, name)
            with open(fpath, "r", encoding="utf-8") as f_in:
                for line in f_in:
                    entry = line.split(SEP)
                    try:
                        if entry[0].lower() not in stop_words:
                            values = (entry[0].lower(), entry[1], int(entry[2]), int(entry[3]))
                            c.execute("insert into terms values (?, ?, ?, ?);", values)
                    except Exception as e:
                        print(e)
                        print("Bad line: ", entry)
    conn.commit()
    print("Populating terms took %s seconds" % (time.time() - start))
    insert_terms_idf(conn)
    insert_terms_tf(conn)

# Inserts values into sentences table
# conn: connection to the database
# reset: a bool, if True drops old table and creates new one 
def insert_sentences(conn, reset):
    start = time.time()
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    if reset:
        c.executescript("""
                        drop table if exists sentences;
                        create table sentences (
                            doc_id      char(8),
                            sent_id     int,
                            sentence    text,
                            primary key (doc_id,sent_id)        
                        );
                        """)
        conn.commit()

    # iterate through files in sentences directory
    for root, dirs, files in os.walk("..\sentences"):
        for name in files:
            data = []
            fpath = os.path.join(root, name)
            with open(fpath, "r", encoding="utf-8") as f_in:
                for line in f_in:
                    entry = line.split(SEP)
                    try:
                        values = (entry[0], int(entry[1]), entry[2].strip('\n'))
                        c.execute("insert into sentences values (?, ?, ?);", values)
                    except Exception as e:
                        print(e)
                        print("Bad line: ", entry)
    conn.commit()
    print("Populating sentences took %s seconds" % (time.time() - start))


# Inserts values into stop_words table
# conn: connection to the database
# words_file: filename of a .txt file containing the stop words
def insert_stop_words(conn, words_file):
    start = time.time()
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

    with open(words_file, "r", encoding="utf-8") as f_in:
        for term in f_in:
            term = term.strip()
            c.execute("insert into stop_words values (?);", (term,))
    conn.commit()
    print("Populating stop_words took %s seconds" % (time.time() - start))


# Inserts values into doc_lengths table
# conn: connection to the database
def insert_doc_lengths(conn):
    start = time.time()
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    # get all sentences for docs
    c.execute(""" select sentence, doc_id
                    from sentences
                """)
    
    doc_lengths = defaultdict(lambda: 0)
    # count words by splitting on spaces
    for row in c:
        sentence = row[0].split()
        doc_id = row[1]
        doc_lengths[doc_id] += len(sentence)

    c.executescript("""
                    drop table if exists doc_lengths;
                    create table doc_lengths (
                        doc_id      char(8),
                        length      int,
                        primary key (doc_id)
                    );
                    """)

    for doc_id, length in doc_lengths.items():
        c.execute("insert into doc_lengths values (?, ?);", (doc_id, length))
    conn.commit()
    print("Populating doc_lengths took %s seconds" % (time.time() - start))

# Inserts values into terms_idf table
# conn: connection to the database
def insert_terms_idf(conn):
    start = time.time()
    c = conn.cursor()
    c2 = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    c.executescript("""
                    drop table if exists terms_idf;
                    create table terms_idf (
                        term      text,
                        idf       float,
                        idf2      float,
                        primary key (term)
                    );
                    """)
    conn.commit()

    c.execute("select count(doc_id) from doc_lengths;")
    total_docs = c.fetchone()[0]

    # get idfs from en-idf
    # inserts original idf (not normalized)
    en_idf = {}
    with open("en-idf.txt", "r", encoding="utf-8") as f_in:
        for line in f_in:
            term, idf = line.split("@en:")
            idf = float(idf.strip())
            en_idf[term] = idf

    c.execute(""" select term, count(distinct doc_id)
            from terms
            group by term
    """)

    for row in c:
        term = row[0]
        idf = get_idf(row[1], total_docs)
        idf2 = None
        try:
            idf2 = en_idf[term]
        except:
            idf2 = None
        finally:
            values = (term, idf, idf2)
            c2.execute("insert into terms_idf values (?, ?, ?);", values)
    conn.commit()
    print("Populating terms_idf took %s seconds" % (time.time() - start))

# Inserts values into term_tf table
# conn: connection to the database
def insert_terms_tf(conn):
    start = time.time()
    c = conn.cursor()
    c2 = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    c.executescript("""
                    drop table if exists terms_tf;
                    create table terms_tf (
                        term        text,
                        doc_id      char(8),
                        frequency   float,
                        primary key (term, doc_id)
                    );
                    """)

    c.execute(""" select t.term, t.doc_id, count(*), d.length
                    from terms t, doc_lengths d
                    where t.doc_id = d.doc_id
                    group by t.term, t.doc_id;
            """)
    for row in c:
        values = (row[0], row[1], row[2] / row[3])
        c2.execute("insert into terms_tf values (?, ?, ?);", values)
    conn.commit()
    print("Populating terms_tf took %s seconds" % (time.time() - start))

# Inserts values into ents_idf table
# conn: connection to the database
def insert_ents_idf(conn):
    start = time.time()
    c = conn.cursor()
    c2 = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    c.executescript("""
                    drop table if exists ents_idf;
                    create table ents_idf (
                        entity      text,
                        idf       float,
                        idf2      float,
                        primary key (entity)
                    );
                    """)

    c.execute("select count(doc_id) from doc_lengths;")
    total_docs = c.fetchone()[0]

    # get idfs from en-idf
    # inserts original idf (not normalized)
    en_idf = {}
    with open("en-idf.txt", "r", encoding="utf-8") as f_in:
        for line in f_in:
            ent, idf = line.split("@en:")
            idf = float(idf.strip())
            en_idf[ent] = idf

    c.execute(""" select entity, count(distinct doc_id)
                from entities
                group by entity
        """)
    for row in c:
        ent = row[0]
        idf = get_idf(row[1], total_docs)
        idf2 = None
        try:
            idf2 = en_idf[ent]
        except:
            idf2 = None
        finally:
            values = (ent, idf, idf2)
            c2.execute("insert into ents_idf values (?, ?, ?);", values)
    conn.commit()    
    print("Populating ents_idf took %s seconds" % (time.time() - start))

# Inserts values into ents_tf table
# conn: connection to the database
def insert_ents_tf(conn):
    start = time.time()
    c = conn.cursor()
    c2 = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    c.executescript("""
                    drop table if exists ents_tf;
                    create table ents_tf (
                        entity        text,
                        doc_id      char(8),
                        frequency   float,
                        primary key (entity, doc_id)
                    );
                    """)

    c.execute(""" select e.entity, e.doc_id, count(*), d.length
                    from entities e, doc_lengths d
                    where e.doc_id = d.doc_id
                    group by e.entity, e.doc_id;
            """)
    for row in c:
        values = (row[0], row[1], row[2] / row[3])
        c2.execute("insert into ents_tf values (?, ?, ?);", values)
    conn.commit()
    print("Populating ents_tf took %s seconds" % (time.time() - start))