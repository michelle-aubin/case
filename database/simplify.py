# Gets just terms and doc ids from all_tokens.txt and writes to tokens.txt

def main():
    with open("tokens_for_db.txt", "r", encoding="utf-8") as f_in:
        with open("tokens.txt", "w", encoding="utf-8") as f_out:
            for line in f_in:
                data = line.split("|!|")
                f_out.write(data[0] + "|!|" + data[1] + "\n")

main()