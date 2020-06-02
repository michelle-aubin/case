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


def process(nlp, batch_id, texts, f):
 #   print("Processing batch", batch_id)
    proc_time = time.time()
    f_batch = f + "batch" + str(batch_id) + ".txt"
    f_batch_path = Path(f_batch)
    if f_batch_path.exists():
        return None
    with open(f_batch, "w", encoding="utf-8") as f_out:
        for doc, doc_id in nlp.pipe(texts, as_tuples=True):
            build_output(doc, doc_id, f_out)
  #  print("Processing batch %d took %s seconds" % (batch_id, time.time()-proc_time))


def build_output(doc, doc_id, f_out):
    for token in doc:
        # only take non entities and non punctuation
        # and take lowercase form
        if token.ent_iob == 2 and not token.is_punct:
            output = token.lower_ + "|" + doc_id + "\n"
            f_out.write(output)


@plac.annotations(
   start=("Doc ID to start on.", "positional", None, int),
   end=("Doc ID to end on (included in NER results).", "positional", None, int),
   batch_size=("Number of docs to run through pipeline at once", "positional", None, int),
   num_p=("Number of processes to use", "positional", None, int)   
)
def main(start, end, batch_size, num_p):
    print("Loading model...")
    model_time = time.time()
    nlp = spacy.load("../custom_model3")
    print("Loading model took %s seconds --" % (time.time() - model_time))
    # make directories for ner-results and sentences
    out_dir = "token-results/" + "token" + str(start) + "-" + str(end) + "/"
    out_path = Path(out_dir)
    if not out_path.exists():
        out_path.mkdir(parents=True)

    print("Reading documents...")
    read_time = time.time()
    with open("../clean_metadata.csv", "r", encoding="utf-8") as f_meta:
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
    tasks = (do(i, batch, out_dir) for i, batch in enumerate(partitions))
    executor(tasks)


if __name__ == "__main__":
    start_time = time.time()
    plac.call(main)
    print("-- %s seconds --" % (time.time() - start_time))

# def main():
#     conn = sqlite3.connect("cord19.db")
#     c = conn.cursor()
#     c.execute("PRAGMA foreign_keys = ON;")
#     conn.commit()

#     print("Loading model...")
#     nlp = spacy.load("../custom_model3")

#     with open("non_entities.txt", "w", encoding="utf-8") as f_out:
#         c.execute("SELECT * FROM sentences;")
#         for row in c:
#             doc_id = row[0]
#            # sent_id = row[1]
#             text = row[2]
#             doc = nlp(text)
#             for token in doc:
#                 # only take non entities and non punctuation
#                 # and take lowercase form
#                 if token.ent_iob == 2 and not token.is_punct:
#                     output = token.lower_ + "|" + doc_id + "\n"
#                     f_out.write(output)
    
# main()