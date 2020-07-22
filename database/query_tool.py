import sqlite3
import spacy
from bm25 import get_idf, get_idfs, calc_summand
import time
from constants import PROX_R
import plac
from xml.dom import minidom
from proximity import get_spans, get_max_prox_score
import heapq as hq

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
    terms = set()
    doc = nlp(query)
    print("Terms found:")
    for token in doc:
        # if token is not a punct and not a stop word
        if not token.is_punct and token.text.lower() not in stop_words:
            print("\t%s" % token.text)
            terms.add(token.text.lower())
    return list(terms)

# Returns a dictionary with terms as keys and sorted lists of (doc id, term frequency) tuples as values
# terms: query terms
# c: cursor for database
def get_posting_lists(terms, c):
    posting_lists = {}
    doc_sets = {}
    for term in terms:
        # gets list of (doc id, frequency) tuples sorted by doc id
        c.execute("select doc_id, frequency from terms_tf where term = :term;", {"term": term})
        posting_lists[term] = c.fetchall()
        # get set of docs for each term
        doc_sets[term] = {tup[0] for tup in posting_lists[term]}
    if len(terms) == 1:
        return posting_lists
    # only keep docs that have all of the terms
    intersect_docs = set.intersection(*doc_sets.values())
    for term in terms:
        new_list = []
        for tup in posting_lists[term]:
            if tup[0] in intersect_docs:
                new_list.append(tup)
        posting_lists[term] = new_list
    return posting_lists

@plac.annotations(
   input_file=("Input file of queries", "positional", None, str),
   output_file=("Output file", "positional", None, str), 
   run_tag=("Tag representing the run", "positional", None, str),
   db_name=("Database name", "positional", None, str)
)
def main(input_file, output_file, run_tag, db_name):
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
    doc_scores = []

    print("Loading model...")
    nlp = spacy.load("../custom_model3", disable=['bc5cdr_ner', 'bionlp13cg_ner', 'entity_ruler', 'web_ner'])

    for tnum, query in enumerate(queries):
        print("Getting scores...")
        start = time.time()
        tnum += 1
        terms = get_terms(query, nlp, stop_words)
        idfs = get_idfs(terms, c, max_idf)
        posting_lists = get_posting_lists(terms, c)

        # traverse the posting lists at the same time to get bm25 score
        for i in range(len(posting_lists[terms[0]])):
            score = 0
            for term, plist in posting_lists.items():
                tf = plist[i][1]
                idf = idfs[term]
                doc_id = plist[i][0]
                c.execute("select length from doc_lengths where doc_id = :doc_id;", {"doc_id":doc_id})
                doc_length = c.fetchone()[0]
                score += calc_summand(tf, idf, doc_length, avg_length)
            # make 100 a parameter
            if len(doc_scores) < 100:
                hq.heappush(doc_scores, (score, doc_id))
            else:
                if score > doc_scores[0][0]:
                    hq.heappushpop(doc_scores, (score, doc_id))
            
        # get proximity score
        for doc_id in doc_scores:
            spans = get_spans(doc_id, terms, c)
            prox_score = get_max_prox_score(spans, set(terms))
            doc_scores[doc_id] = PROX_R * bm25_score + (1-PROX_R) * prox_score

        # sort in descending order of score
        doc_scores = hq.nlargest(len(doc_scores), doc_scores)

        print("Took %.2f seconds to get scores" % (time.time() - start))
        i = 0
        with open(output_file, "a") as f_out:
            for tup in doc_scores:
                doc = tup[1]
                score = tup[0]
                # return max 1000 docs
                if i >= 1000 or not doc_scores:
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