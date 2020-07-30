import csv
import sqlite3

def main():
    in_db = set()
    conn = sqlite3.connect("database/cord19-round4.db")
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    c.execute("select doc_id from doc_lengths;")
    for row in c:
        in_db.add(row[0])
    
    with open(r'../cord-19_2020-07-16/2020-07-16/metadata.csv', "r", encoding="utf-8") as f_meta:
        with open("clean-metadata-2020-07-16.csv", "w", encoding="utf-8", newline='') as f_out:
            seen = set()
            clean_metadata = csv.writer(f_out)
            clean_metadata.writerow(['cord_uid','title','abstract','json_file'])
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
                    title = row.get('title')
                    abstract = row.get('abstract')
                    if cord_uid not in seen and cord_uid not in in_db:
                        seen.add(cord_uid)
                        clean_metadata.writerow([cord_uid, title, abstract, urls[0]])
                    else:
                        print("Duplicate or already in db %s" % cord_uid)

main()
