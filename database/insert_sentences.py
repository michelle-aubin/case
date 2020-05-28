import sqlite3
import os

def main():
    conn = sqlite3.connect("cord19.db")
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    # iterate through files in sentences directory
    os.chdir('../sentences')
    bad_docs = set()
    for root, dirs, files in os.walk("."):
        for name in files:
            data = []
            fpath = os.path.join(root, name)

            with open(fpath, "r", encoding="utf-8") as f_in:
                print(fpath)
                # start_ind = 0
                # data = f_in.read()
                # while start_ind >= 0:
                #     doc_id_end = data.find("|", start_ind)
                #     doc_id = data[start_ind:doc_id_end]
                #     start_ind = doc_id_end + 1
                for line in f_in:
                    if line.find("|"):
                        entry = line.split("|")
                    #  print(entry)
                        try:
                            if entry[0] in bad_docs:
                                continue
                            values = (entry[0], int(entry[1]), entry[2].strip('\n'))
                           # c.execute("insert into sentences values (?, ?, ?);", values)
                        except:
                            if len(entry[0]) == 8 and entry[0] not in bad_docs:
                                print(entry[0])
                                bad_docs.add(entry[0])
    if bad_docs:
        os.chdir('../')
        with open("bad_docs.txt", "a", encoding="utf-8") as f:
            for doc in bad_docs:
                f.write(doc + '\n')


    
#    conn.commit()
                    


    # c.execute("SELECT * FROM sentences;")
    # sents = c.fetchall()
    # for sent in sents:
    #     print(sent)


main()
    