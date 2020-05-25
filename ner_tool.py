import csv
import urllib.request, json 
import spacy
import time
import plac
import numpy as np

URL = "https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/latest/"


def read_url(url_str, cord_uid, articles):
 #   url_start = time.time()
    with urllib.request.urlopen(URL + url_str) as url:
     #   print("URL Request took %s seconds --" % (time.time() - url_start))
        data = json.loads(url.read().decode())
        if data.get("abstract"):
            texts = [entry.get("text") for entry in data.get("abstract")]
        else:
            texts = []
        for entry in data.get("body_text"):
            texts.append(entry.get("text"))
        full = " ".join(texts)
        articles.append((full, cord_uid))

def process(nlp, texts, f, size, num_p):
    with open(f, "w", encoding="utf-8") as f_out:
        for doc, doc_id in nlp.pipe(texts, as_tuples=True, n_process=num_p, batch_size=size):
            build_output(doc, doc_id, f_out)
#    articles.clear()

def build_output(doc, doc_id, f_out):
  #  output_start = time.time()
    print("Writing output for Doc %s" % doc_id)
    for sent_id, sent in enumerate(doc.sents):
        ents = list(sent.ents)
        for ent in ents:
            # entity name|type|doc id (row num in metadata.csv)|sent id|offset start|offset end
            data_list = [ent.text, ent.label_, doc_id, str(sent_id), 
                            str(ent.start_char-ent.sent.start_char), 
                            str(ent.end_char-ent.sent.start_char)]
            data_str = "|".join(data_list) + "\n"
            f_out.write(data_str)
 #   print("Building output took %s seconds --" % (time.time() - output_start))

@plac.annotations(
   start=("Doc ID to start on.", "positional", None, int),
   end=("Doc ID to end on (included in NER results).", "positional", None, int),
   batch_size=("Number of docs to run through pipeline at once", "positional", None, int),
   num_p=("Number of processes to use", "positional", None, int)
)
def main(start, end, batch_size, num_p):
    print("Loading model...")
    model_time = time.time()
    nlp = spacy.load("custom_model3", disable=["tagger"])
    print("Loading model took %s seconds" % (time.time() - model_time))
    out_file = "ner-results/" + "ner" + str(start) + "-" + str(end) +".txt"
    # get data
    with open("metadata.csv", "r", encoding="utf-8") as f_meta:
        articles = []
        metadata = csv.DictReader(f_meta)
        count = 0
        print("Reading documents...")
        read_time = time.time()
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
                urls = pmc_url.split("; ")
            if urls:
                read_url(urls[0], row.get("cord_uid"), articles)
    print("Reading documents took %s seconds" % (time.time() - read_time))
    print("Processing documents...")
    # do ner and write to file
    process(nlp, articles, out_file, batch_size, num_p)



if __name__ == "__main__":
    start_time = time.time()
    plac.call(main)
    print("-- %s seconds --" % (time.time() - start_time))
            

