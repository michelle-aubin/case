import csv
import json 
import spacy
import time
import plac
from joblib import Parallel, delayed
from functools import partial
from spacy.util import minibatch
from pathlib import Path

SEP = "|!|"
DP_PATH = "../2020-06-19/"

# returns a tuple of (full text, cord uid) for a doc given
# a dictionary from the metadata
def get_text_id_tuple(row_dict):
    texts = []
    doc_id = row_dict['cord_uid']
    title = row_dict['title']
    if title:
        # add a period to the title
        texts.append(title + '.')
    abstract = row_dict['abstract']
    if abstract:
        texts.append(abstract)
    with open(DP_PATH+row_dict['json_file'], "r", encoding="utf-8") as f_json:
        full_text_dict = json.load(f_json)
        for paragraph_dict in full_text_dict['body_text']:
            text = paragraph_dict['text'].replace('\n', '')
            texts.append(text)
    full = " ".join(texts)
    return (full, doc_id)  

# run batch through pipeline and create output files for the batch
def process(nlp, batch_id, texts, f_ent, f_sent, f_term):
    # create entities output file
    ent_f_batch = f_ent + "batch" + str(batch_id) + ".txt"
    ent_f_batch_path = Path(ent_f_batch)
    # if exists then another process has made it
    if ent_f_batch_path.exists():
        return None
    # create sentences output file
    sent_f_batch = f_sent + "batch" + str(batch_id) + ".txt"
    sent_f_batch_path = Path(sent_f_batch)
    if sent_f_batch_path.exists():
        return None
    # create terms output file
    term_f_batch = f_term + "batch" + str(batch_id) + ".txt"
    term_f_batch_path = Path(term_f_batch)
    if term_f_batch_path.exists():
        return None
    # run batch through pipeline
    with open(ent_f_batch, "w", encoding="utf-8") as ent_f_out, open(sent_f_batch, "w", encoding="utf-8") as sent_f_out, open(term_f_batch, "w", encoding="utf-8") as term_f_out:
        for doc, doc_id in nlp.pipe(texts, as_tuples=True):
            build_output(doc, doc_id, ent_f_out, sent_f_out, term_f_out)
 
# creates output and writes to files
def build_output(doc, doc_id, ent_f_out, sent_f_out, term_f_out):
    for sent_id, sent in enumerate(doc.sents):
        # doc id|!|sent id|!|sentence
        data_list = [doc_id, str(sent_id), sent.text]
        sent_data_str = SEP.join(data_list) + "\n"
        sent_f_out.write(sent_data_str)

        for token in sent:
            # check that token is a term
            if token.ent_iob == 2 and not token.is_punct:
              # term|!|doc id|!|sent id|!|offset start
                data_list = [token.lower_, doc_id, str(sent_id), 
                            str(token.idx - sent.start_char)]
                data_str = SEP.join(data_list) + "\n"
                term_f_out.write(data_str)

        ents = list(sent.ents)
        for ent in ents:
            # entity name|!|type|!|doc id|!|sent id|!|offset start
            data_list = [ent.lower_, ent.label_, doc_id, str(sent_id), 
                            str(ent.start_char-ent.sent.start_char)]
            data_str = SEP.join(data_list) + "\n"
            ent_f_out.write(data_str)

@plac.annotations(
   start=("Doc ID to start on.", "positional", None, int),
   end=("Doc ID to end on (included in results).", "positional", None, int),
   batch_size=("Number of docs to run through pipeline at once", "positional", None, int),
   num_p=("Number of processes to use", "positional", None, int)   
)
# creates text files used to populate entities, sentences, and terms table in the databse
def main(start, end, batch_size, num_p):
    # load spacy pipeline
    print("Loading model...")
    model_time = time.time()
    nlp = spacy.load("custom_model3", disable=["tagger"])
    print("Loading model took %s seconds --" % (time.time() - model_time))
 
    # make directories for entities, sentences and terms
    ent_out_dir = "entities/" + "ent" + str(start) + "-" + str(end) + "/"
    ent_f_out_path = Path(ent_out_dir)
    if not ent_f_out_path.exists():
        ent_f_out_path.mkdir(parents=True)
    sent_out_dir = "sentences/" + "sent" + str(start) + "-" + str(end) + "/"
    sent_f_out_path = Path(sent_out_dir)
    if not sent_f_out_path.exists():
        sent_f_out_path.mkdir(parents=True)
    term_out_dir = "terms/" + "term" + str(start) + "-" + str(end) + "/"
    term_f_out_path = Path(term_out_dir)
    if not term_f_out_path.exists():
        term_f_out_path.mkdir(parents=True)

    # make list of (full text, cord uid) tuples
    print("Reading documents...")
    read_time = time.time()
    with open("clean-metadata-2020-06-19.csv", "r", encoding="utf-8") as f_meta:
        articles = []
        metadata = csv.DictReader(f_meta)
        for row_num, row in enumerate(metadata):
            if row_num < start:
                continue
            elif row_num > end:
                break
            articles.append(get_text_id_tuple(row))
    print("Reading %d documents took %s seconds" % (len(articles), time.time() - read_time))
    # batch docs and send to pipeline with multiprocessing
    partitions = minibatch(articles, size=batch_size)
    executor = Parallel(n_jobs=num_p, backend="multiprocessing", prefer="processes") 
    do = delayed(partial(process, nlp))
    tasks = (do(i, batch, ent_out_dir, sent_out_dir, term_out_dir) for i, batch in enumerate(partitions))
    executor(tasks)


if __name__ == "__main__":
    start_time = time.time()
    plac.call(main)
    print("-- %s seconds --" % (time.time() - start_time))