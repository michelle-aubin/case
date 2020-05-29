import sqlite3
import os
import time

def main():
    conn = sqlite3.connect("cord19.db")
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    # iterate through files in sentences directory
  #  os.chdir('../sentences')
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
                        values = (entry[0], entry[1], int(entry[2]), int(entry[3]), int(entry[4]), int(entry[5].strip('\n')))
                        c.execute("insert into sentences values (?, ?, ?);", values)
                    except Exception as e:
                        print(e)
                        print("Bad line: ", entry)
        com_time = time.time()
        conn.commit()
        print("Committing took %s seconds" % (time.time() - com_time))


main()
    