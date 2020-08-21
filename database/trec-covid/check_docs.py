import sqlite3

def main():

    conn = sqlite3.connect(r'..\cord19.db')
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    docs_rnd4 = set()

    with open(r'round3\docids-rnd3.txt', "r") as f_in:
        for line in f_in:
            doc_id = line.strip()
            docs_rnd4.add(doc_id)

    count_not = 0
    count = 0

    docs_db = set()
    c.execute("select doc_id from doc_lengths;")
    for row in c:
        docs_db.add(row[0])

    docs_to_add = docs_db - docs_rnd4
    for doc in docs_to_add:
        print(doc)



main()