import sqlite3
import spacy
from bm25 import get_idf, get_idfs, calc_summand
import time
from constants import PROX_R, DOCS_K
import plac
from xml.dom import minidom
from proximity import get_spans, get_max_prox_score
from priority_queue import PQueue
from collections import defaultdict

# Returns a list of queries
# input_file: a trec-covid .xml file containing the queries
def get_queries(input_file):
    queries = []
    xml_doc = minidom.parse(input_file)
    topics = xml_doc.getElementsByTagName('topic')
    for topic in topics:
        q = topic.getElementsByTagName('query')[0].childNodes[0].data
        queries.append(q)
    return queries

# Returns a set of query terms given a query string
def get_terms(query, nlp, stop_words):
    terms = set()
    doc = nlp(query)
    for token in doc:
        # if token is not a punct and not a stop word
        if not token.is_punct and token.text.lower() not in stop_words:
            terms.add(token.text.lower())
    for ent in doc.ents:
        terms.add(ent.text.lower())
    return terms

# Given a term, returns a set of synonyms including the term
def get_synonyms(term):
    synonyms = [
                {"covid-19", "sars-cov-2", "covid 19"},
                {"coronavirus", "common cold"},
                {"covid", "covid-19", "covid 19"}
                ]
    for tup in synonyms:
        if term in tup:
            return tup
    return None


# Returns a dictionary with terms as keys and sorted lists of (doc id, term frequency) tuples as values
# terms: query terms
# c: cursor for database
def get_posting_lists(terms, c):
    posting_lists = {}
    syns_used = defaultdict(lambda: set())
    for term in terms:
        synonyms = get_synonyms(term)
        if synonyms:
            syn_posting = defaultdict(lambda: 0)
            for syn_term in synonyms:
                c.execute("select doc_id, frequency from tf where term = :term;", {"term": syn_term})
                for tup in c:
                    doc_id = tup[0]
                    freq = tup[1]
                    syn_posting[doc_id] += freq
                    syns_used[doc_id].add(syn_term)
            posting_lists[term] = sorted(syn_posting.items())
        else:
            # gets list of (doc id, frequency) tuples sorted by doc id
            c.execute("select doc_id, frequency from tf where term = :term;", {"term": term})
            posting_lists[term] = c.fetchall()
        if not posting_lists[term]:
            posting_lists.pop(term)
    return posting_lists, syns_used

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
    # get dictionary of doc id and doc lengths
    doc_lengths = {}
    c.execute("select doc_id, length from doc_lengths;")
    for row in c:
        doc_lengths[row[0]] = row[1]
    # get total num of docs
    total_docs = len(doc_lengths)
    # get average doc length
    c.execute("select avg(length) from doc_lengths;")
    avg_length = c.fetchone()[0]
    # get max idf for normalizing idfs from en-idf.txt
    max_idf = get_idf(1, total_docs)


    print("Loading model...")
    nlp = spacy.load("../custom_model3")# , disable=['bc5cdr_ner', 'bionlp13cg_ner', 'entity_ruler', 'web_ner'])

    for tnum, query in enumerate(queries):
        doc_scores = PQueue(DOCS_K)
        print("Getting scores...")
        start = time.time()
        tnum += 1
        print(tnum, query)
        terms = get_terms(query, nlp, stop_words)
        idfs = get_idfs(terms, c, max_idf)
        posting_lists, syns_used = get_posting_lists(terms, c)
        indices = {term: 0 for term in posting_lists}
        terms = {term for term in posting_lists}
        print("Query terms", terms)
        # traverse the posting lists at the same time to get bm25 score
        while indices:
            postings = {}
            score = 0
            for term, index in indices.items():
                postings[term] = posting_lists[term][index][0]
            smallest_doc = min(postings.values())
            for term, doc_id in postings.items():
                if doc_id == smallest_doc:
                    doc_length = doc_lengths[doc_id]
                    idf = idfs[term]
                    tf = posting_lists[term][indices[term]][1]
                    score += calc_summand(tf, idf, doc_length, avg_length)
                    indices[term] += 1
                    # traversed the entire posting list
                    if indices[term] >= len(posting_lists[term]):
                        indices.pop(term)
            doc_scores.add_doc_score(smallest_doc, score)
            
        if doc_scores.get_items():
            # get proximity score
            for i, tup in enumerate(doc_scores.get_items()):
                bm25_score = tup[0]
                doc_id = tup[1]
                if syns_used:
                    spans = get_spans(doc_id, terms | syns_used[doc_id], c)
                    prox_score = get_max_prox_score(spans, terms | syns_used[doc_id])
                else:
                    spans = get_spans(doc_id, terms, c)
                    prox_score = get_max_prox_score(spans, terms)
                new_score = (PROX_R * bm25_score + (1-PROX_R) * prox_score, doc_id)
                doc_scores.assign_new_score(i, new_score)

            # sort in descending order of score
            doc_scores.sort_descending()

            print("Took %.2f seconds to get scores" % (time.time() - start))
            i = 0
            with open(output_file, "a") as f_out:
                for tup in doc_scores.get_items():
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
        else:
            print("No documents returned.")

if __name__ == "__main__":
    start_time = time.time()
    plac.call(main)
    print("-- %s seconds --" % (time.time() - start_time))