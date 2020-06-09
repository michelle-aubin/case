from collections import defaultdict
import math
from bm25 import get_idf

def main():
    with open("stopWords.txt", "r", encoding="utf-8") as f_in:
        stop_words = {term.strip() for term in f_in}

    word_counts = defaultdict(lambda: 0)
    print("Reading file...")
    with open("sorted_tokens.txt", "r", encoding="utf-8") as f_in:
        for line in f_in:
            word = line.split("|!|")[0]
            # word doesn't have any alpha characters - dont include
            if not word.islower():
                continue
            if word not in stop_words:
                word_counts[word] +=1
            

    print("Building output...")
    with open("idf.txt", "w", encoding="utf-8") as f_out:    
        for word, count in sorted(word_counts.items(), key=lambda item: item[1], reverse=True):
            idf = get_idf(count)
            f_out.write(word + "|!|" + str(idf) + "\n")


    # to count how many docs are in the input file
    # doc_counts = defaultdict(lambda: 0)
    # with open("tokens.txt", "r", encoding="utf-8") as f_in:
    #     print("Reading file...")
    #     for line in f_in:
    #         doc = line.split("|")[1]
    #         doc_counts[doc] = 0
    # print("There are %d documents in tokens.txt" % len(doc_counts))
                

main()