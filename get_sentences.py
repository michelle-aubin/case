import urllib.request, json 
import spacy
import csv
import time
import plac
from joblib import Parallel, delayed
from functools import partial
from spacy.util import minibatch
from pathlib import Path

URL = "https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/latest/"

def read_url(url_str, cord_uid, articles):
 #   url_start = time.time()
    with urllib.request.urlopen(URL + url_str) as url:
     #   print("URL Request took %s seconds --" % (time.time() - url_start))
        data = json.loads(url.read().decode())
        if data.get("abstract"):
            texts = [entry.get("text").replace('\n', '') for entry in data.get("abstract")]
        else:
            texts = []
        for entry in data.get("body_text"):
            texts.append(entry.get("text").replace('\n', ''))
        full = " ".join(texts)
        articles.append((full, cord_uid))

def process(nlp, batch_id, texts, f):
    print("Processing batch", batch_id)
    proc_time = time.time()
    f_batch = f + "batch" + str(batch_id) + ".txt"
    f_batch_path = Path(f_batch)
    if f_batch_path.exists():
        return None
    with open(f_batch, "w", encoding="utf-8") as f_out:
        for doc, doc_id in nlp.pipe(texts, as_tuples=True):
            build_output(doc, doc_id, f_out)
    print("Processing batch %d took %s seconds" % (batch_id, time.time()-proc_time))

def build_output(doc, doc_id, f_out):
    for sent_id, sent in enumerate(doc.sents):
            # doc id|sentence id|sentence
            data_list = [doc_id, str(sent_id), sent.text]
            data_str = "|".join(data_list) + "\n"
            f_out.write(data_str)


@plac.annotations(
   start=("Doc ID to start on.", "positional", None, int),
   end=("Doc ID to end on (included in results).", "positional", None, int),
   batch_size=("Number of docs to run through pipeline at once", "positional", None, int),
   num_p=("Number of processes to use", "positional", None, int)   
)
def main(start, end, batch_size, num_p):
    print("Loading model...")
    nlp = spacy.load("custom_model3", disable=["tagger", "web_ner", "bc5cdr_ner", 
                                                "bionlp13cg_ner", "entity_ruler"])
    # make sentences directory if it doesn't exist
    out_dir = "sentences/" + "sent" + str(start) + "-" + str(end) + "/"
    f_out_path = Path(out_dir)
    if not f_out_path.exists():
        f_out_path.mkdir(parents=True)
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
    print(articles)
    # partitions = minibatch(articles, size=batch_size)
    # executor = Parallel(n_jobs=num_p, backend="multiprocessing", prefer="processes") 
    # do = delayed(partial(process, nlp))
    # tasks = (do(i, batch, out_dir) for i, batch in enumerate(partitions))
    # executor(tasks)

if __name__ == "__main__":
    start_time = time.time()
    plac.call(main)
    print("-- %s seconds --" % (time.time() - start_time))