import itertools

def main():
    rank1 = ["urs5z4l1", "mcyeyl4s", "trcisop6", "js2ppypr", "6g1y3eyy"]
    rank2 = ["urs5z4l1","mcyeyl4s","js2ppypr","xiv9vxdp","mgz7w9y4"]
    all_docs = # intersection with no repetition
    # get all pairs from all_docs (can use itertools.combinations)
    # for each pair, get indices of the two items in the pair from both
    # ranked lists
    # if item1 index > item2 index in both lists, good
    # else add one to distance
    # if an item is not in a list, give it index 6
    kendall_tau_distance(rank1,rank2)

def kendall_tau_distance(rank1, rank2):
    pairs = itertools.combinations(range(1, len(rank1)+1), 2)
    distance = 0
    for i, j in pairs:
        a = 

main()