import sqlite3
import spacy
from bm25 import get_score, get_idf, get_idfs
import time
from constants import PROX_R
import plac
from xml.dom import minidom
from proximity import get_spans, get_max_prox_score

# Returns a dictionary with doc ids as key and score of 0 as values
# c: cursor for database
def get_doc_ids(c, docs_file):
    with open(docs_file, "r") as f_in:
        valid = {line.strip() for line in f_in}
    doc_scores = {}
    # all docs
    c.execute("select doc_id from doc_lengths;")
    for row in c:
        doc_id = row[0]
        if doc_id in valid:
            doc_scores[doc_id] = 0

    # only docs that are related to covid19
    # c.execute("select distinct doc_id from entities where type = \"CORONAVIRUS\";")
    # for row in c:
    #     doc_id = row[0]
    #     doc_scores[doc_id] = 0

    return doc_scores

# Returns a list of queries
def get_queries(input_file):
    queries = []
    xml_doc = minidom.parse(input_file)
    topics = xml_doc.getElementsByTagName('topic')
    for topic in topics:
        queries.append(topic.getElementsByTagName('query')[0].childNodes[0].data)
    return queries

# Returns lists of terms given a query
def get_terms(query, nlp, stop_words):
    terms = []
    doc = nlp(query)
    print("Terms found:")
    for token in doc:
        # if token is not a punct and not a stop word
        if not token.is_punct and token.text.lower() not in stop_words:
            print("\t%s" % token.text)
            terms.append(token.text.lower())
    return terms

@plac.annotations(
   input_file=("Input file of queries", "positional", None, str),
   output_file=("Output file", "positional", None, str), 
   run_tag=("Tag representing the run", "positional", None, str),
   valid_docs=("Text file of valid doc ids to use", "positional", None, str),
   db_name=("Database name", "positional", None, str)
)
def main(input_file, output_file, run_tag, valid_docs, db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    print("Gathering some data...")
    # get stop words
    stop_words = set()
    c.execute("select word from stop_words;")
    for row in c:
        stop_words.add(row[0])

    # get valid docs to include in ranking
    doc_scores = get_doc_ids(c, valid_docs)
    # get queries from input file
    queries = get_queries(input_file)
    # get total num of docs
    c.execute("select count(doc_id) from doc_lengths;")
    total_docs = c.fetchone()[0]
    # get average doc length
    c.execute("select avg(length) from doc_lengths;")
    avg_length = c.fetchone()[0]
    # get max idf for normalizing idfs from en-idf.txt
    max_idf = get_idf(1, total_docs)

    print("Loading model...")
    nlp = spacy.load("../custom_model3", disable=['bc5cdr_ner', 'bionlp13cg_ner', 'entity_ruler', 'web_ner'])

    for tnum, query in enumerate(queries):
        tnum += 1
        terms = get_terms(query, nlp, stop_words)
        idfs = get_idfs(terms, c, max_idf)

        print("Getting scores...")
        start = time.time()
        for doc_id in doc_scores:
            terms_set = set(terms)
            spans = get_spans(doc_id, terms, c)
            prox_score = get_max_prox_score(spans, terms_set)
            bm25_score = get_score(doc_id, terms, total_docs, avg_length, idfs, c)
            doc_scores[doc_id] = PROX_R * bm25_score + (1-PROX_R) * prox_score
            return

        print("Took %.2f seconds to get scores" % (time.time() - start))
        i = 0
        with open(output_file, "a") as f_out:
            for doc, score in sorted(doc_scores.items(), key=lambda item: item[1], reverse=True):
                # return max 1000 docs
                if i >= 1000 or score == 0:
                    # no docs returned
                    if i == 0:
                        # make dummy list
                        output_vals = [str(tnum), "Q0", doc, str(i+1), str(score), run_tag, "\n"]
                        f_out.write("\t".join(output_vals))
                    break
                i += 1
                output_vals = [str(tnum), "Q0", doc, str(i), str(score), run_tag, "\n"]
                f_out.write("\t".join(output_vals))

if __name__ == "__main__":
    start_time = time.time()
    plac.call(main)
    print("-- %s seconds --" % (time.time() - start_time))