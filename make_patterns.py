import json
import spacy

# make a .jsonl file of patterns that can be used in the EntityRuler
def main():
    new_labels = set()
    with open("chosen_types_from_CORD-NER.txt", "r") as label_file:
        for label in label_file:
            new_labels.add(label.strip())

    with open('CORD-NER/CORD-NER-ner.json', 'r') as data_file:
        ents_seen = set()
        for data_line in data_file:
            data = json.loads(data_line)
            print("Doc %d" % data.get("doc_id"))
            sents = data.get("sents")
            for sent in sents:
                ents_list = sent.get("entities")
            # for entity in ent list, tokenize it
            # write the tokens and ent type in pattern form
            # can do additional checking: if type in (new types that aren't
            # from the pretrained models) then add it, else don't add it
                for ent in ents_list:
                    ent_type = ent.get("type")
                    ent_text = ent.get("text")
                    if ent_type in new_labels and ent_text not in ents_seen:
                        ents_seen.add(ent_text)
                        tokens = ent_text.split(" ")
                        for token in tokens:
                            tokens[tokens.index(token)] = token.split("_")
                        tokens_list = []
                        for t in tokens:
                            for token in t:
                                tokens_list.append({"LOWER": token})
                        pattern = {"label": ent_type, "pattern": tokens_list}
                        # just split text on spaces instead of using spacy to tokenize?
                        with open("patterns_wo_disease_or_syndrome.jsonl", "a") as f:
                            json.dump(pattern, f)
                            f.write("\n")

main()