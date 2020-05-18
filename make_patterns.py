import json

# make a .jsonl file of patterns that can be used in the EntityRuler
def main():
    nlp = spacy.load("en_core_web_sm", disable=["ner"])
    # disable tagger too? jsut need pipeline components to tokenize
   with open('CORD-NER/CORD-NER-ner.json', 'r') as data_file:
        for data_line in data_file:
            data = json.loads(data_line)
            ents_list = data.get("entities")
            # for entity in ent list, tokenize it
            # write the tokens and ent type in pattern form
            # can do additional checking: if type in (new types that aren't
            # from the pretrained models) then add it, else don't add it

main()