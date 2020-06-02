import time


def main():
    with open("tokens.txt", "r", encoding="utf-8") as f_in:
        with open("frequencies.txt", "w", encoding="utf-8") as f_out:
            prev_word = f_in.readline().split("|")[0]
            count = 1
            for line in f_in:
                word = line.split("|")[0]
                # word doesn't have any alpha characters - dont include
                if not word.islower():
                    continue
                if word == prev_word:
                    count += 1
                else:
                    #
                    output = "{:<8}{}\n".format(count, prev_word)
                    print(output)
                    f_out.write(output)
                    count = 1
                    prev_word = word

                

main()