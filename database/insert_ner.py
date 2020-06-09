import sqlite3
import os
import time

def main():
    conn = sqlite3.connect("cord19.db")
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    drop_start = time.time()
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
    print("Dropping old table took %s seconds" % (time.time() - drop_start))
    # iterate through files in sentences directory
  #  os.chdir('../sentences')
    insert_time = time.time()
    for root, dirs, files in os.walk("../ner-results"):
        for name in files:
            data = []
            fpath = os.path.join(root, name)
            print(fpath)
            with open(fpath, "r", encoding="utf-8") as f_in:
                for line in f_in:
                    entry = line.split("|")
                   # print(entry)
                    try:
                        # entity|type|doc_id|sent_id|start|end
                        values = (entry[0].lower(), entry[1], entry[2], int(entry[3]), int(entry[4]))
                        c.execute("insert into entities values (?, ?, ?, ?, ?);", values)
                    except Exception as e:
                        print(e)
                        print("Bad line: ", entry)
        conn.commit()
    print("Populating table took %s seconds" % (time.time() - insert_time))


main()
    