import plac
import sqlite3

@plac.annotations(
   db_name=("Database name", "positional", None, str)
)
def main(db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c2 = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    c2.execute("select entity, doc_id, sent_id, start from entities;")
    for row in c2:
        splitted_ent = row[0].split(" ")
        # entity is just one word
        if len(splitted_ent) == 1:
            try:
                c.execute("insert into terms values (?, ?, ?, ?);", row)
            except Exception as e:
                print(e)
                print(row)
        # entity is more than 1 word
        else:
            for i, entity in enumerate(splitted_ent):
                if i == 0:
                    values = (entity, row[1], row[2], row[3])
                    try:
                        c.execute("insert into terms values (?, ?, ?, ?);", values)
                    except Exception as e:
                        print(e)
                        print(row)
                else:
                    start = row[3]
                    for j in range(0, i):
                        start += len(splitted_ent[j]) + 1
                    values = (entity, row[1], row[2], start)
                    try:
                        c.execute("insert into terms values (?, ?, ?, ?);", values)
                    except Exception as e:
                        print(e)
                        print(row)

    conn.commit()

if __name__ == "__main__":
    plac.call(main)
