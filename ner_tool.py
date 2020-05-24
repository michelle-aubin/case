import csv
import urllib.request, json 
import spacy
import time
import plac
import numpy as np

URL = "https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/latest/"



def read_url(url_str, cord_uid, articles):
    url_start = time.time()
    with urllib.request.urlopen(URL + url_str) as url:
        print("URL Request took %s seconds --" % (time.time() - url_start))
        json_start = time.time()
        data = json.loads(url.read().decode())
        print("JSON load took %s seconds --" % (time.time() - json_start))
        if data.get("abstract"):
            texts = [entry.get("text") for entry in data.get("abstract")]
        else:
            texts = []
        for entry in data.get("body_text"):
            texts.append(entry.get("text"))
        full = " ".join(texts)
        # do batches of documents
        articles.append((full, cord_uid))

@plac.annotations(
   start=("Doc ID to start on.", "positional", None, int),
   end=("Doc ID to end on (included in NER results).", "positional", None, int),
   batch_size=("Number of docs to run through pipeline at once", "positional", None, int)
)
def main(start, end, batch_size):
    model_time = time.time()
    nlp = spacy.load("custom_model3" , disable=["tagger"])
    print("Loading model took %s seconds --" % (time.time() - model_time))
    out_file = "test-results/" + "test" + str(start) + "-" + str(end) +".txt"
    with open("metadata.csv", "r", encoding="utf-8") as f_meta:
        with open(out_file, "w", encoding="utf-8") as f_out:
            articles = []
            metadata = csv.DictReader(f_meta)
            for row_num, row in enumerate(metadata):
                if row_num < start:
                    continue
                elif row_num > end:
                    break
                urls = []
                pdf_url = row.get("pdf_json_files")
                pmc_url = row.get("pmc_json_files")
                if pdf_url:
                    urls = pdf_url.split("; ")
                elif pmc_url:
                    urls = pdf_url.split("; ")
                if urls:
                    read_url(urls[0], row.get("cord_uid"), articles)
                    if row_num != 0 and (row_num + 1) % batch_size == 0:
                        pipe_start = time.time()
                        docs = list(nlp.pipe(articles, as_tuples=True))
                        print("NLP pipe took %s seconds --" % (time.time() - pipe_start))
                        output_start = time.time()
                        for doc, doc_id in docs:
                            print("Doc %s" % doc_id)
                            for sent_id, sent in enumerate(doc.sents):
                                ents = list(sent.ents)
                                for ent in ents:
                                    # entity name|type|doc id (row num in metadata.csv)|sent id|offset start|offset end
                                    data_list = [ent.text, ent.label_, doc_id, str(sent_id), 
                                                    str(ent.start_char-ent.sent.start_char), 
                                                    str(ent.end_char-ent.sent.start_char)]
                                    data_str = "|".join(data_list) + "\n"
                                    f_out.write(data_str)
                        print("Building output took %s seconds --" % (time.time() - output_start))
                        articles.clear() 

if __name__ == "__main__":
    start_time = time.time()
    plac.call(main)
    print("-- %s seconds --" % (time.time() - start_time))
            

