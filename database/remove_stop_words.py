
def main():
    stop_words = set()
    with open("stopWords.txt", "r") as f_stop:
        for line in f_stop:
            stop_words.add(line.strip())
    with open("frequencies2.txt", "w", encoding="utf-8") as f_out:
        with open("frequencies.txt", "r", encoding="utf-8") as f_in:
            for line in f_in:
                num = line[0:8]
                word = line[8:].strip()
                if word not in stop_words:
                   f_out.write(num+word+"\n")
                

main()