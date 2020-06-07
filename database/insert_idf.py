import sqlite3
import math
import time

def main():
    conn = sqlite3.connect("cord19.db")
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    with open("idf.txt", "r", encoding="utf-8") as f_in:
        for line in f_in:
            term, idf = line.split("|!|")
            idf = float(idf.strip())
            c.execute("insert into idf values (?, ?);", (term, idf))
    conn.commit()

main()