import csv
import urllib.request, json 
import spacy
import time
import plac
import numpy as np
from joblib import Parallel, delayed
from functools import partial
from spacy.util import minibatch

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

def process(nlp, batch_id, texts, f):
    print("Processing batch", batch_id)
    f_batch = f + "-" + str(batch_id) + ".txt"
    with open(f_batch, "w", encoding="utf-8") as f_out:
        for doc, doc_id in nlp.pipe(texts, as_tuples=True):
            build_output(doc, doc_id, f_out)
#    articles.clear()

def build_output(doc, doc_id, f_out):
  #  output_start = time.time()
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
   batch_size=("Number of docs to run through pipeline at once", "positional", None, int)
)
def main(start, end, batch_size):
    print("Loading model...")
    model_time = time.time()
    nlp = spacy.load("custom_model3")
    print("Loading model took %s seconds --" % (time.time() - model_time))
    out_file = "ner-results/" + "ner" + str(start) + "-" + str(end)
    print("Reading documents...")
    read_time = time.time()
    with open("clean_metadata.csv", "r", encoding="utf-8") as f_meta:
        articles = []
        metadata = csv.DictReader(f_meta)
        for row_num, row in enumerate(metadata):
            if row_num < start:
                continue
            elif row_num > end:
                break
            read_url(row.get("json_file"), row.get("cord_uid"), articles)
    print("Reading %d documents took %s seconds" % (len(articles), time.time() - read_time))
    partitions = minibatch(articles, size=20)
    executor = Parallel(n_jobs=4, backend="multiprocessing", prefer="processes") 
    do = delayed(partial(process, nlp))
    tasks = (do(i, batch, out_file) for i, batch in enumerate(partitions))
    executor(tasks)


if __name__ == "__main__":
    start_time = time.time()
    plac.call(main)
    print("-- %s seconds --" % (time.time() - start_time))