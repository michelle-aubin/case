import itertools

# Returns kendall tau distance given two ranked lists
def kendall_tau_distance(rank1, rank2):
    # get all pairs
    all_docs = list(set(rank1) | set(rank2))
    pairs = itertools.combinations(all_docs, 2)
    distance = 0
    for doc1, doc2 in pairs:
        # print("For pair %s and %s:" % (doc1, doc2))
        # print("\tList1: %s rank %d \t %s rank %d" % (doc1, get_rank(doc1, rank1), doc2, get_rank(doc2, rank1)))
        # print("\tList2: %s rank %d \t %s rank %d" % (doc1, get_rank(doc1, rank2), doc2, get_rank(doc2, rank2)))
        a = get_rank(doc1, rank1) - get_rank(doc2, rank1)
        b = get_rank(doc1, rank2) - get_rank(doc2, rank2)
        # print("\ta = %d \t b = %d" % (a,b))
        # if a and b are diff signs then pair is discordant
        if (a * b) < 0:
            # print("\tDiscordant")
            distance += 1
    # print("Distance: %d" % distance)
    return distance
        

# gets the rank of doc in the rank list
# if doc is not in the list, returns a rank of 5 (outside of list)
def get_rank(doc, rank_list):
    try:
        rank = rank_list.index(doc)
    except ValueError:
        rank = 5
    finally:
        return rank
