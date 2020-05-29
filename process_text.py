import csv
import urllib.request, json 
import spacy
import time
import plac
import numpy as np
from joblib import Parallel, delayed
from functools import partial
from spacy.util import minibatch
from pathlib import Path

URL = "https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/latest/"



def read_url(url_str, cord_uid, articles):
    try:
        with urllib.request.urlopen(URL + url_str) as url:
            data = json.loads(url.read().decode())
            if data.get("abstract"):
                texts = [entry.get("text").replace('\n', '') for entry in data.get("abstract")]
            else:
                texts = []
            for entry in data.get("body_text"):
                texts.append(entry.get("text").replace('\n', ''))
            full = " ".join(texts)
            articles.append((full, cord_uid))
    except Exception as e:
        print("Could not read doc %s" % cord_uid)
        return


def process(nlp, batch_id, texts, f_ent, f_sent):
 #   print("Processing batch", batch_id)
    proc_time = time.time()
    ent_f_batch = f_ent + "batch" + str(batch_id) + ".txt"
    ent_f_batch_path = Path(ent_f_batch)
    if ent_f_batch_path.exists():
        return None
    sent_f_batch = f_sent + "batch" + str(batch_id) + ".txt"
    sent_f_batch_path = Path(sent_f_batch)
    if sent_f_batch_path.exists():
        return None
    with open(ent_f_batch, "w", encoding="utf-8") as ent_f_out:
        with open(sent_f_batch, "w", encoding="utf-8") as sent_f_out:
            for doc, doc_id in nlp.pipe(texts, as_tuples=True):
                build_output(doc, doc_id, ent_f_out, sent_f_out)
  #  print("Processing batch %d took %s seconds" % (batch_id, time.time()-proc_time))

# creates .txt files of rows for sentence table and entity table
def build_output(doc, doc_id, ent_f_out, sent_f_out):
    for sent_id, sent in enumerate(doc.sents):
        # doc id|sent id|sentence
        data_list = [doc_id, str(sent_id), sent.text]
        sent_data_str = "|".join(data_list) + "\n"
        sent_f_out.write(sent_data_str)
        ents = list(sent.ents)
        for ent in ents:
            # entity name|type|doc id|sent id|offset start|offset end
            data_list = [ent.text, ent.label_, doc_id, str(sent_id), 
                            str(ent.start_char-ent.sent.start_char), 
                            str(ent.end_char-ent.sent.start_char)]
            data_str = "|".join(data_list) + "\n"
            ent_f_out.write(data_str)

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
    print("Loading model took %s seconds --" % (time.time() - model_time))
    # make directories for ner-results and sentences
    ent_out_dir = "ner-results/" + "ner" + str(start) + "-" + str(end) + "/"
    ent_f_out_path = Path(ent_out_dir)
    if not ent_f_out_path.exists():
        ent_f_out_path.mkdir(parents=True)
    sent_out_dir = "sentences/" + "sent" + str(start) + "-" + str(end) + "/"
    sent_f_out_path = Path(sent_out_dir)
    if not sent_f_out_path.exists():
        sent_f_out_path.mkdir(parents=True)

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
    partitions = minibatch(articles, size=batch_size)
    executor = Parallel(n_jobs=num_p, backend="multiprocessing", prefer="processes") 
    do = delayed(partial(process, nlp))
    tasks = (do(i, batch, ent_out_dir, sent_out_dir) for i, batch in enumerate(partitions))
    executor(tasks)


if __name__ == "__main__":
    start_time = time.time()
    plac.call(main)
    print("-- %s seconds --" % (time.time() - start_time))