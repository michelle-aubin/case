import csv

def main():
    with open("metadata.csv", "r", encoding="utf-8") as f_meta:
        with open("clean_metadata.csv", "w", encoding="utf-8") as f_out:
            f_out.write("cord_uid,json_file\n")
            articles = []
            metadata = csv.DictReader(f_meta)
            for row_id, row in enumerate(metadata):
                print(row_id)
                urls = []
                pdf_url = row.get("pdf_json_files")
                pmc_url = row.get("pmc_json_files")
                if pdf_url:
                    urls = pdf_url.split("; ")
                elif pmc_url:
                    urls = pmc_url.split("; ")
                if urls:
                    out_str = row.get("cord_uid") + "," + urls[0] +"\n"
                    f_out.write(out_str)

main()
