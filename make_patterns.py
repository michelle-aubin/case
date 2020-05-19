import json
import spacy

# make a .jsonl file of patterns that can be used in the EntityRuler
def main():
    # what labels should I add?
    new_labels = {"CORONAVIRUS",
                "VIRAL_PROTEIN",
                "LIVESTOCK",
                "WILDLIFE",
                "EVOLUTION",
                "PHYSICAL_SCIENCE",
                "SUBSTRATE",
                "MATERIAL",
                "IMMUNE_RESPONSE"}
    nlp = spacy.load("en_core_web_sm", disable=["ner"])
    # disable tagger too? jsut need pipeline components to tokenize
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
                        tokens = ent_text.split()
                        tokens_list = []
                        for t in tokens:
                            tokens_list.append({"LOWER": t})
                        pattern = {"label": ent_type, "pattern": tokens_list}
                        # just split text on spaces instead of using spacy to tokenize?
                        with open("patterns.jsonl", "a") as f:
                            json.dump(pattern, f)
                            f.write("\n")

main()