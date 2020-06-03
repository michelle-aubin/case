from collections import defaultdict
import csv

def main():
    docs = set()
    with open("tokens.txt", "r", encoding="utf-8") as f_in:
        print("Reading file...")
        for line in f_in:
            doc = line.split("|!|")[1]
            docs.add(doc)
    all_docs = set()
    with open("../clean_metadata.csv", "r", encoding="utf-8") as f_meta:
        metadata = csv.DictReader(f_meta)
        for row in metadata:
            all_docs.add(row.get("cord_uid"))
    
    with open("missing_docs.txt", "w", encoding="utf-8") as f_out:
        for doc in docs:
            if doc not in all_docs:
                f_out.write(doc)

main()