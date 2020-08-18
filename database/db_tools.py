import sqlite3
import os
import time
from constants import SEP
from collections import defaultdict
from bm25 import get_idf
import csv

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
                                        foreign key (doc_id,sent_id) references sentences on delete cascade
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
                            foreign key (doc_id,sent_id) references sentences on delete cascade
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
    insert_idf(conn)
    insert_tf(conn)

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
                            primary key (doc_id,sent_id),
                            foreign key (doc_id) references doc_lengths on delete cascade        
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
def insert_doc_lengths(conn, reset):
    start = time.time()
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    if reset:
        c.executescript("""
                        drop table if exists doc_lengths;
                        create table doc_lengths (
                            doc_id      char(8),
                            length      int,
                            primary key (doc_id)
                        );
                        """)
        conn.commit()

    # iterate through files in sentences directory
    for root, dirs, files in os.walk("..\lengths"):
        for name in files:
            data = []
            fpath = os.path.join(root, name)
            with open(fpath, "r", encoding="utf-8") as f_in:
                for line in f_in:
                    entry = line.split(SEP)
                    try:
                        values = (entry[0], int(entry[1]).strip('\n'))
                        c.execute("insert into doc_lengths values (?, ?);", values)
                    except Exception as e:
                        print(e)
                        print("Bad line: ", entry)

    conn.commit()
    print("Populating doc_lengths took %s seconds" % (time.time() - start))

# Inserts values into idf table
# conn: connection to the database
def insert_idf(conn):
    start = time.time()
    c = conn.cursor()
    c2 = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    c.execute("drop table if exists idf;")
    c.executescript("""
                    create table idf (
                        term      text,
                        idf       float,
                        primary key (term)
                    );
                    """)
    conn.commit()

    c.execute("select count(doc_id) from doc_lengths;")
    total_docs = c.fetchone()[0]

    # # idf for terms
    c.execute(""" select term, count(distinct doc_id)
            from terms
            group by term
    """)
    for row in c:
        term = row[0]
        idf = get_idf(row[1], total_docs)
        values = (term, idf)
        c2.execute("insert into idf values (?, ?);", values)
    conn.commit()
    # idf for entities
    c.execute(""" select entity, count(distinct doc_id)
            from entities
            group by entity
    """)
    for row in c:
        entity = row[0]
        idf = get_idf(row[1], total_docs)
        values = (entity, idf)
        try:
            c2.execute("insert into idf values (?, ?);", values)
        except Exception:
            continue
    conn.commit()
    print("Populating idf took %s seconds" % (time.time() - start))

# Inserts values into term_tf table
# conn: connection to the database
def insert_tf(conn):
    start = time.time()
    c = conn.cursor()
    c2 = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    c.executescript("""
                    drop table if exists tf;
                    create table tf (
                        term        text,
                        doc_id      char(8),
                        frequency   float,
                        primary key (term, doc_id),
                        foreign key (doc_id) references doc_lengths on delete cascade
                    );
                    """)

    # tf for terms
    c.execute(""" select t.term, t.doc_id, count(*), d.length
                    from terms t, doc_lengths d
                    where t.doc_id = d.doc_id
                    group by t.term, t.doc_id;
            """)
    for row in c:
        values = (row[0], row[1], row[2] / row[3])
        c2.execute("insert into tf values (?, ?, ?);", values)
    conn.commit()
    # tf for entities
    c.execute(""" select e.entity, e.doc_id, count(*), d.length
                    from entities e, doc_lengths d
                    where e.doc_id = d.doc_id
                    group by e.entity, e.doc_id;
            """)
    for row in c:
        values = (row[0], row[1], row[2] / row[3])
        try:
            c2.execute("insert into tf values (?, ?, ?);", values)
        except Exception:
            continue
    conn.commit()
    print("Populating tf took %s seconds" % (time.time() - start))

# Removes docs that are not in a given metadata file
def remove_docs(conn):
    f_in = input("Enter metadata file for remove docs: ")
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    c2 = conn.cursor()
    c2.execute("PRAGMA foreign_keys = ON;")
    docs = set()
    with open(f_in, "r", encoding="utf-8") as f_meta:
        metadata = csv.DictReader(f_meta)
        for row in metadata:
            urls = []
            pdf_url = row.get('pdf_json_files')
            pmc_url = row.get('pmc_json_files')
            if pmc_url:
                urls = pmc_url.split("; ")
            elif pdf_url:
                urls = pdf_url.split("; ")
            if urls:
                cord_uid = row.get('cord_uid')
                docs.add(cord_uid)
        
        count = 0
        c.execute("select doc_id from doc_lengths;")
        for row in c:
            doc_id = row[0]
            if doc_id not in docs:
                c2.execute("delete from doc_lengths where doc_id = :doc_id", {"doc_id": doc_id})
                c2.execute("delete from entities where doc_id = :doc_id", {"doc_id": doc_id})
                c2.execute("delete from terms where doc_id = :doc_id", {"doc_id": doc_id})
                c2.execute("delete from sentences where doc_id = :doc_id", {"doc_id": doc_id})
                count += 1
        conn.commit()
        # could recalculate idfs
        print("Deleted %d docs" % count)