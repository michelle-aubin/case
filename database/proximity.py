from constants import PROX_K

# algorithm for detect spans taken from https://www.microsoft.com/en-us/research/publication/viewing-term-proximity-from-a-different-perspective/

# Given a document, prepares necessary data for finding spans and returns a list of spans for the document
# doc_id: doc id of the document
# query_terms: set of query terms
# c: cursor for database
def get_spans(doc_id, query_terms, c):
    c.execute("select term from terms where doc_id = :doc_id;", {"doc_id": doc_id})
    # represent the doc as an ordered sequence of terms
    doc_terms = []
    for row in c:
        doc_terms.append(row[0])
    # get ordered chain of query term hits
    chain_of_hits = get_chain_of_hits(query_terms, doc_terms)
    print(doc_terms)
    print(chain_of_hits)
    # get spans
    return detect_spans(chain_of_hits, query_terms, doc_terms)


# Returns all query term occurences in the doc as a list of nodes aka
# tuples (position, query term) with the position being the index of the query term in doc_terms
# query_terms: set of query terms
# doc_terms: ordered sequence of terms in the doc            
def get_chain_of_hits(query_terms, doc_terms):
    chain = []
    for i, term in enumerate(doc_terms):
        if term in query_terms:
            chain.append((i, term))
    return chain

# Calculates the spans for a given document and returns spans as a list
# chain_of_hits: ordered chain of query term occurences
# query_terms: set of query terms
# doc_terms: ordered sequence of terms in the doc
def detect_spans(chain_of_hits, query_terms, doc_terms):
    spans = []
    # get first node (first query term hit)
    try:
        curr_first_node = chain_of_hits[0]
    except IndexError:
        curr_first_node = None
    curr_node = curr_first_node
    if (curr_node != None):
        next_node = get_next_node(curr_node, chain_of_hits)
        while next_node != None:
            # case 1 and 2
            if (distance(curr_node, next_node) > PROX_K) or (curr_node[1] == next_node[1]):
            #    print("Curr node %s, next node %s" % (curr_node, next_node))
                spans.append(save_span(curr_first_node, curr_node, doc_terms))
                curr_first_node = next_node
            else:
                repeated_node = find_repeated_node(curr_node, next_node, curr_first_node, chain_of_hits)
                # case 3
                if repeated_node != None:
                    # get the next node of the repeated node
                    r_next_node = get_next_node(repeated_node, chain_of_hits)
                    # look at distance between repeated node and its next
                    # and distance between current node and its next
                    # then split span into two spans based on larger distance
                    if (distance(repeated_node, r_next_node) > distance(curr_node, next_node)):
                        # span ends on the repeated node
                        spans.append(save_span(curr_first_node, repeated_node, doc_terms))
                        curr_first_node = r_next_node
                    else:
                        spans.append(save_span(curr_first_node, curr_node, doc_terms))
                        curr_first_node = next_node
            curr_node = next_node
            next_node = get_next_node(curr_node, chain_of_hits)
        spans.append(save_span(curr_first_node, curr_node, doc_terms))
    return spans

                
        
# Returns the next node given a current node
# node: the current node
# chain_of_hits: ordered chain of query term occurences
def get_next_node(node, chain_of_hits):
    next_node_idx = chain_of_hits.index(node) + 1
    try:
        next_node = chain_of_hits[next_node_idx]
    except IndexError:
        next_node = None
    finally:
        return next_node

# Returns the distance in number of terms separating node1 and node2
def distance(node1, node2):
    node1_pos = node1[0]
    node2_pos = node2[0]
    return abs(node2_pos - node1_pos)

# Returns a list representing a span that contains the start node 
# and end node terms, and all terms in between the two
# start_node: starting query term node of the span
# end_node: ending query term node of the span
# doc_terms: ordered sequence of terms in the doc 
def save_span(start_node, end_node, doc_terms):
    span = []
    start_pos = start_node[0]
    end_pos = end_node[0]
    # span contains just one query term, will be of length k with no query end term
    if start_pos == end_pos:
        for i in range(start_pos, start_pos + PROX_K):
            try:
                span.append(doc_terms[i])
            except IndexError:
                break
    else:
        for i in range(start_pos, end_pos + 1):
            span.append(doc_terms[i])
    return span

# Looks for a node that has the same term as search_node in the range
# of start and current
# If it doesn't find any, returns None
# current: the current node (end of search range)
# start: the start node of the span (start of search range)
# search_node: the node that has the term which we are searching for
def find_repeated_node(current, search_node, start, chain_of_hits):
    repeated_node = start;
    while (repeated_node != current) and (repeated_node[1] != search_node[1]):
        repeated_node = get_next_node(repeated_node, chain_of_hits)
    # found a repeated node
    if (repeated_node != current):
        return repeated_node;
    else:
        return None

# Returns the max proximity score for a document
# spans: spans representin the document
# query_terms: set of query terms
def get_max_prox_score(spans, query_terms):
    max_score = -1
    for span in spans:
        score = get_prox_score(span, query_terms)
        if score > max_score:
            max_score = score
    return max_score

# Returns the proximity score of a span
# span: the span
# query_terms: set of query terms
def get_prox_score(span, query_terms):
    # num of different query terms in the span
    num_qts_unique = len(query_terms & set(span))
    # num of query terms
    num_qts_total = len(query_terms)
    # num of terms in the span
    num_terms_total = len(span)
    return (num_qts_unique / num_qts_total) * (num_qts_unique / num_terms_total)