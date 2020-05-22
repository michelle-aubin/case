import csv
import urllib.request, json 
import spacy
import time
import plac

URL = "https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/latest/"


@plac.annotations(
   start=("Doc ID to start on.", "positional", None, int),
   end=("Doc ID to end on (included in NER results).", "positional", None, int)
)
def main(start, end):
    model_time = time.time()
    nlp = spacy.load("custom_model3", disable=["tagger"])
    print("Loading model took %s seconds --" % (time.time() - model_time))
    out_file = "test" + str(start) + "-" + str(end) +".txt"
    with open("metadata.csv", "r", encoding="utf-8") as f_meta:
        with open(out_file, "w", encoding="utf-8") as f_out:
            metadata = csv.DictReader(f_meta)
            row_num = -1
            for row in metadata:
                row_num += 1
                if row_num < start:
                    continue
                elif row_num > end:
                    break
                print("Doc %d" % row_num)
                pdf_url = row.get("pdf_json_files")
                if pdf_url:
                    pdf_urls = pdf_url.split("; ")
                    url_start = time.time()
                    with urllib.request.urlopen(URL + pdf_urls[0]) as url:
                        print("URL Request took %s seconds --" % (time.time() - url_start))
                        json_start = time.time()
                        data = json.loads(url.read().decode())
                        print("JSON load took %s seconds --" % (time.time() - json_start))
                        texts = [entry.get("text") for entry in data.get("abstract")]
                        for entry in data.get("body_text"):
                            texts.append(entry.get("text"))
                        pipe_start = time.time()
                        docs = list(nlp.pipe(texts, batch_size=4))
                        print("NLP pipe took %s seconds --" % (time.time() - pipe_start))
                        output_start = time.time()
                        for doc in docs:
                            par_id = docs.index(doc)
                            sent_id = -1
                            for sent in doc.sents:
                                sent_id += 1
                                ents = list(sent.ents)
                                for ent in ents:
                                    # entity name|type|doc id (row num in metadata.csv)|paragraph id|sent id|offset start|offset end
                                    data_list = [ent.text, ent.label_, str(row_num), str(par_id), str(sent_id), 
                                                    str(ent.start_char-ent.sent.start_char), 
                                                    str(ent.end_char-ent.sent.start_char)]
                                    data_str = "|".join(data_list) + "\n"
                                  #  f_out.write(data_str)
                        print("Building output took %s seconds --" % (time.time() - output_start))

            

                # paragraph id is entry is index in list of "text" entries in abstract and body
                # ex abstract: [0,1,2], body_text: [3,4,5]     

if __name__ == "__main__":
    start_time = time.time()
    plac.call(main)
    print("-- %s seconds --" % (time.time() - start_time))
            

