
class Wand:
    def __init__(self, query_terms, posting_lists):
        # current document to be considered
        self.cur_doc = 0
        # dictionary of term as key and posting list as value
        self.posting_lists = posting_lists
        # list of query terms
        self.query_terms = query_terms
        # dictionary of term as key and index of current posting in its posting list as value
        self.posting = {term: 0 for term in query_terms}
        # dictionary of term as key and the term's upper bound score as value
        self.ubt_values = {term: self.get_UBt(term) for term in query_terms}
        # last doc id (largest doc id) out of all of the posting lists
        self.last_doc_id = self.get_last_doc_id()


    # Get's the upper bound score contribution for a term
    # aka the max term frequency in the term's posting list
    # posting_list: a list of (doc_id, term frequency) tuples for the term
    def get_UBt(self, term):
        posting_list = self.posting_lists[term]
        return max(tup[1] for tup in posting_list)

    # Returns the last doc id (largest doc id) out of all of the posting lists
    def get_last_doc_id(self):
        last_doc_id = "0"
        for posting_list in self.posting_lists.values():
            doc = posting_list[-1][0]
            if doc > last_doc_id:
                last_doc_id = doc
        return last_doc_id

    def next(self, threshold):
        while True:
            self.sort()
            # find the pivot term
            pivot_term = self.find_pivot_term(threshold)
            # no more docs left so return None
            if not pivot_term:
                return None
            # get the pivot doc
            pivot = self.get_posting(term)
            # no more docs left so return None
            if pivot == self.last_doc_id:
                return None
            # pivot has already been considered
            if pivot <= self.cur_doc:
                # advance one of the preceding terms' index
                aterm = self.pick_term(terms[0:index(pivot_term)])
                self.increase_posting_index(aterm)
            else:
                # all terms preceeding pivot_term belong to the pivot
                if (self.get_posting(posting[terms[0]])):
                    self.cur_doc = pivot
                    return self.cur_doc
                # not enough mass yet on pivot
                else:
                    # advance one of the preceeding terms
                    aterm = self.pick_term(terms[0:index(pivot_term)])
                    self.increase_posting_index(aterm)
                

    def pick_term(self, terms):
        # pick term that will give the biggest skip
        # guessing that it'll be term with shortest posting list
        lengths = {}
        for term in terms:
            length = len(self.posting_lists[term])
            lengths[term] = length
        for term, length in sorted(lengths.items(), key=lambda item: item[1]):
            return term

            



    # Sorts the query terms list in non decreasing order of document id
    def sort(self):
        sorted_terms = []
        posting_docs = {term: self.get_posting(term) for term in self.query_terms}
        for term, doc in sorted(posting_docs.items(), key=lambda item: item[1]):
            sorted_terms.append(term)
        self.query_terms = sorted_terms

    # Sums the UBt for each term until the sum is >= threshold
    # Returns the term that makes the sum >= threshold
    def find_pivot_term(self, threshold):
        accumulated_ubt = 0
        for term in self.query_terms:
            accumulated_ubt += self.ubt_values[term]
            if accumulated_ubt >= threshold:
                return term
        return None


    # Returns current posting in term's posting list
    def get_posting(self, term):
        index = self.posting[term]
        posting_list = self.posting_lists[term]
        return posting_list[index]

    # Increases term's posting list index until it points to a doc
    # that is larger than the current doc
    def increase_posting_index(self, term):
        doc = self.get_posting(term)
        while doc <= self.cur_doc:
            self.posting[term] += 1



