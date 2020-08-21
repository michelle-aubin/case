import csv
import sqlite3
import plac


@plac.annotations(
   meta_f=("Path to CORD-19 Metadata input file", "positional", None, str),
   date=("Date of CORD-19 version [YYYY-MM-DD]", "positional", None, str),
   db=("Path to database", "option", None, str)
)
def main(meta_f, date, db):
    in_db = set()
    if db:
        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute("PRAGMA foreign_keys = ON;")
        conn.commit()
        c.execute("select doc_id from doc_lengths;")
        for row in c:
            in_db.add(row[0])
    
    with open(meta_f, "r", encoding="utf-8") as f_meta:
        with open("clean-metadata-"+date+".csv", "w", encoding="utf-8", newline='') as f_out:
            seen = set()
            clean_metadata = csv.writer(f_out)
            clean_metadata.writerow(['cord_uid','title','abstract','json_file', 'url'])
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
                    web_url = row.get('url')
                    if cord_uid not in seen and cord_uid not in in_db:
                        seen.add(cord_uid)
                        clean_metadata.writerow([cord_uid, title, abstract, urls[0], web_url])

if __name__ == "__main__":
    plac.call(main)