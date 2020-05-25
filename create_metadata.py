import csv

def main():
    with open("metadata.csv", "r", encoding="utf-8") as f_meta:
        with open("clean_metadata.csv", "w", encoding="utf-8") as f_out:
            seen = set()
            f_out.write("cord_uid,json_file\n")
            articles = []
            metadata = csv.DictReader(f_meta)
            for row_id, row in enumerate(metadata):
                urls = []
                pdf_url = row.get("pdf_json_files")
                pmc_url = row.get("pmc_json_files")
                if pdf_url:
                    urls = pdf_url.split("; ")
                elif pmc_url:
                    urls = pmc_url.split("; ")
                if urls:
                    cord_uid = row.get("cord_uid")
                    if cord_uid not in seen:
                        seen.add(cord_uid)
                        out_str = cord_uid + "," + urls[0] +"\n"
                        f_out.write(out_str)
                    else:
                        print("Duplicate %s" % cord_uid)

main()
