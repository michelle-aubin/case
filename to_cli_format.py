from spacy.gold import biluo_tags_from_offsets, spans_from_biluo_tags, docs_to_json
import plac
import pickle
import spacy
import json
import time

# converts training data to BILUO format 

@plac.annotations(
   train_file=("Training data file name", "positional", None, str)
)
def main(train_file):
    nlp = spacy.load("en_core_sci_sm", disable=["ner"])
    docs = []
    with open (train_file, 'rb') as fp:
        train_data = pickle.load(fp)
    # create doc objects out of training data
    for text, annot in train_data:
        doc = nlp(text)
        tags = biluo_tags_from_offsets(doc, annot['entities'])
        entities = spans_from_biluo_tags(doc, tags)
        doc.ents = entities
        docs.append(doc)
    # convert list of docs into json format used by spacy train command
    json_data = docs_to_json(docs)

    train_file_split = train_file.split("-")
    file_name = 'cli-training-data' + '-' + train_file_split[2] +'.json'
    with open(file_name, 'w') as json_file:
        json.dump(json_data, json_file)

if __name__ == "__main__":
    start_time = time.time()
    plac.call(main)
    print("-- %s seconds --" % (time.time() - start_time))

