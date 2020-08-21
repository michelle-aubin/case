import sqlite3
import spacy
from collections import defaultdict
import time
from textwrap import wrap
from bm25 import get_idfs, calc_summand
from priority_queue import PQueue
from proximity import get_spans, get_max_prox_score
from constants import PROX_R, DOCS_K

# The search engine
class Case:
    def __init__(self, db_name):
        print("Loading...")
        self.db_conn = sqlite3.connect(db_name)
        self.nlp = spacy.load("custom_model3")
        self.stop_words = self.init_stop_words()
        self.doc_lengths = self.init_doc_lengths()
        self.total_doc_num = len(self.doc_lengths)
        self.avg_doc_length = self.init_avg_doc_length()
        self.print_welcome()

    # Prints a welcome message
    def print_welcome(self):
        print("Welcome to the CORD-19 Alberta Search Engine.")
        print("There are currently %d documents in the database.\n" % (self.total_doc_num))

    # Returns a set of stop words
    def init_stop_words(self):
        c = self.db_conn.cursor()
        stop_words = set()
        c.execute("select word from stop_words;")
        for row in c:
            stop_words.add(row[0])
        return stop_words

    # Returns a dictionary of doc id and doc lengths
    def init_doc_lengths(self):
        c = self.db_conn.cursor()
        doc_lengths = {}
        c.execute("select doc_id, length from doc_lengths;")
        for row in c:
            doc_lengths[row[0]] = row[1]
        return doc_lengths
    
    # Returns the average doc length of documents in the database
    def init_avg_doc_length(self):
        c = self.db_conn.cursor()
        c.execute("select avg(length) from doc_lengths;")
        avg_length = c.fetchone()[0]
        return avg_length

    # Returns a set of query terms given a query string
    def get_terms(self, query):
        terms = set()
        doc = self.nlp(query)
        for token in doc:
            # if token is not a punct and not a stop word
            if not token.is_punct and token.text.lower() not in self.stop_words:
                terms.add(token.text.lower())
        for ent in doc.ents:
            terms.add(ent.text.lower())
        return terms

    # Given a term, returns a set of synonyms including the term
    def get_synonyms(self, term):
        synonyms = [
                    {"covid-19", "sars-cov-2", "covid 19"},
                    {"coronavirus", "common cold"},
                    {"covid", "covid-19", "covid 19"}
                    ]
        for tup in synonyms:
            if term in tup:
                return tup
        return None

    # Returns a dictionary with terms as keys and sorted lists of 
    # (doc id, term frequency) tuples as values
    def get_posting_lists(self, terms):
        c = self.db_conn.cursor()
        posting_lists = {}
        syns_used = defaultdict(lambda: set())
        for term in terms:
            synonyms = self.get_synonyms(term)
            # include posting list for each synonym
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

    # Returns a sorted list of (score, doc id) tuples
    # of the top 25 documents given a query 
    def search(self, query):
        start = time.time()
        c = self.db_conn.cursor()
        doc_scores = PQueue(DOCS_K)
        terms = self.get_terms(query)
        idfs = get_idfs(terms, c)
        posting_lists, syns_used = self.get_posting_lists(terms)
        # get rid of any terms that do not appear in the corpus
        terms = {term for term in posting_lists}
        # used to traverse posting lists
        indices = {term: 0 for term in posting_lists}
        # traverse the posting lists at the same time to get bm25 score for each doc
        while indices:
            postings = {}
            score = 0
            for term, index in indices.items():
                postings[term] = posting_lists[term][index][0]
            smallest_doc = min(postings.values())
            for term, doc_id in postings.items():
                # get bm25 score for a doc
                if doc_id == smallest_doc:
                    doc_length = self.doc_lengths[doc_id]
                    idf = idfs[term]
                    tf = posting_lists[term][indices[term]][1]
                    score += calc_summand(tf, idf, doc_length, self.avg_doc_length)
                    indices[term] += 1
                    # traversed the entire posting list
                    if indices[term] >= len(posting_lists[term]):
                        indices.pop(term)
            doc_scores.add_doc_score(smallest_doc, score)
        # if query has results
        if doc_scores.get_items():
            # get proximity score
            for i, tup in enumerate(doc_scores.get_items()):
                bm25_score = tup[0]
                doc_id = tup[1]
                spans = get_spans(doc_id, terms | syns_used[doc_id], c)
                prox_score = get_max_prox_score(spans, terms | syns_used[doc_id])
                new_score = (PROX_R * bm25_score + (1-PROX_R) * prox_score, doc_id)
                doc_scores.assign_new_score(i, new_score)
            # sort docs in descending order of score
            doc_scores.sort_descending()
            print("Top %d documents retrieved in %.2f seconds" % (len(doc_scores.get_items()), time.time() - start))
            return doc_scores.get_items()
        # query has no results
        else:
            return None

    # 
    # given a list of sorted (score, doc id) tuples        
    def print_query_results(self, results):
        if not results:
            print("No documents match the query!")
        else:
            c = self.db_conn.cursor()
            for i, tup in enumerate(results):
                doc = tup[1]
                c.execute("select sentence from sentences \
                            where doc_id = :doc_id \
                            and sent_id <= 5;", {"doc_id": doc})
                sentences = c.fetchall()
                title = sentences[0][0][0:-1]
                abstract = [sent[0] for sent in sentences[1:]]
                abstract = " ".join(abstract) + ".."
                abstract = wrap(abstract)
                c.execute("select url from urls where doc_id = :doc_id", {"doc_id": doc})
                url = c.fetchone()[0]
                print(title)
                for sent in abstract:
                    print("\t" + sent)
                # print link to the document here
                print("Link:", url)
                command = input("Press enter to view next document or type \"return\" to enter another query\n")
                if command == "return":
                    print("\n")
                    return
                else:
                    print("\n")


