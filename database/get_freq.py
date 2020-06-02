import time
from collections import defaultdict

def main():
    word_counts = defaultdict(lambda: 0)
    print("Reading file...")
    with open("tokens.txt", "r", encoding="utf-8") as f_in:
        for line in f_in:
            word = line.split("|")[0]
            # word doesn't have any alpha characters - dont include
            if not word.islower():
                continue
            word_counts[word] +=1
            
    print("Building output...")
    with open("frequencies.txt", "w", encoding="utf-8") as f_out:    
        for word, count in sorted(word_counts.items(), key=lambda item: item[1], reverse=True):
            output = "{:<8}{}\n".format(count, word)
            f_out.write(output)

        

                

main()