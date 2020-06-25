import csv

def main():
    valid = set()
    with open("docids-rnd4.txt", "r") as f_docs:
        for line in f_docs:
            valid.add(line.strip())
    with open(r'../cord-19_2020-06-19/2020-06-19/metadata.csv', "r", encoding="utf-8") as f_meta:
        with open("clean-metadata-2020-06-19.csv", "w", encoding="utf-8", newline='') as f_out:
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
                    if cord_uid not in seen and cord_uid in valid:
                        seen.add(cord_uid)
                        clean_metadata.writerow([cord_uid, title, abstract, urls[0]])
                    else:
                        print("Duplicate %s" % cord_uid)

main()
