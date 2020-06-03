import time
from collections import defaultdict

def main():
    word_counts = defaultdict(lambda: 0)
    print("Reading file...")
    with open("tokens.txt", "r", encoding="utf-8") as f_in:
        for line in f_in:
            word = line.split("|!|")[0]
            # word doesn't have any alpha characters - dont include
            if not word.islower():
                continue
            word_counts[word] +=1
            
    print("Building output...")
    with open("frequencies3.txt", "w", encoding="utf-8") as f_out:    
        for word, count in sorted(word_counts.items(), key=lambda item: item[1], reverse=True):
            output = "{:<8.2f}{}\n".format((count/58422)*100, word)
            f_out.write(output)


    # to count how many docs are in the input file
    # doc_counts = defaultdict(lambda: 0)
    # with open("tokens.txt", "r", encoding="utf-8") as f_in:
    #     print("Reading file...")
    #     for line in f_in:
    #         doc = line.split("|")[1]
    #         doc_counts[doc] = 0
    # print("There are %d documents in tokens.txt" % len(doc_counts))
                

main()